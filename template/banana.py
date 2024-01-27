import sys
import tempfile
import zipfile

player = %code%

tmp_file = tempfile.NamedTemporaryFile(delete=False)
tmp_file.write(player)

tmp_dir = tempfile.TemporaryDirectory(delete=False)
with zipfile.ZipFile(tmp_file, 'r') as zip_ref:
    zip_ref.extractall(tmp_dir.name)

sys.path.insert(0, tmp_dir.name)
import deck
