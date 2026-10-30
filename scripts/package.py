"""Package only tracked source/evidence, plus a bundle with reproducible Git refs."""
from pathlib import Path
import subprocess
import zipfile
import io

root = Path(__file__).resolve().parents[1]
if subprocess.check_output(['git', 'status', '--porcelain'], cwd=root).strip():
    raise SystemExit('Commit the reviewed submission before packaging')
out = root / 'dist'
out.mkdir(exist_ok=True)
bundle = out / 'repository.bundle'
subprocess.run(['git', 'bundle', 'create', str(bundle), '--all'], cwd=root, check=True)
data = subprocess.check_output(['git', 'archive', '--format=zip', 'HEAD'], cwd=root)
target = out / 'tesselonix-assessment-submission.zip'
with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as dest:
    for item in source.infolist():
        dest.writestr(item, source.read(item.filename))
    dest.write(bundle, 'repository.bundle')
print('Created', target)
