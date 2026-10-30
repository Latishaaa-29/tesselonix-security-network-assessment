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
        bundle.extractall(directory, filter='data')
    run('docker', 'build', '-f', str(Path(directory) / 'lab/app/Dockerfile'),
        '-t', 'tx-microblog:baseline', directory)
run('docker', 'build', '-f', 'lab/app/Dockerfile', '-t', 'tx-microblog:fixed', '.')
run('docker', 'build', '-f', 'lab/db/Dockerfile', '-t', 'tx-db:lab', '.')
run('docker', 'build', '-f', 'lab/client/Dockerfile', '-t', 'tx-tools:lab', '.')
