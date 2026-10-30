"""Build immutable baseline from Git tag, fixed source from current checkout."""
from pathlib import Path
import io
import subprocess
import tarfile
import tempfile

root = Path(__file__).resolve().parents[1]
def run(*args, **kwargs):
    subprocess.run(args, cwd=root, check=True, **kwargs)

archive = subprocess.check_output(['git', 'archive', 'upstream-baseline'], cwd=root)
with tempfile.TemporaryDirectory(prefix='tx-baseline-') as directory:
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        # Python 3.11 releases before 3.11.8 do not expose tarfile's filter API.
        # Write regular Git archive members explicitly, rejecting links/traversal.
        base = Path(directory).resolve()
        for member in bundle:
            target = (base / member.name).resolve()
            if not target.is_relative_to(base):
                raise ValueError('Unsafe archive member')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(bundle.extractfile(member).read())
            else:
                raise ValueError('Unexpected archive link or special file')
    run('docker', 'build', '-f', str(Path(directory) / 'lab/app/Dockerfile'),
        '-t', 'tx-microblog:baseline', directory)
run('docker', 'build', '-f', 'lab/app/Dockerfile', '-t', 'tx-microblog:fixed', '.')
run('docker', 'build', '-f', 'lab/db/Dockerfile', '-t', 'tx-db:lab', '.')
run('docker', 'build', '-f', 'lab/client/Dockerfile', '-t', 'tx-tools:lab', '.')
