import os
import shutil
import zipfile
import tempfile
import pytest
import sys

from components.get_data.wandb_utils.utils import download_file, extract_csv_from_zip

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

def test_download_file_success(monkeypatch, temp_dir):
    url = "http://example.com/test.csv"
    output_path = os.path.join(temp_dir, "test.csv")
    fake_content = b"col1,col2\n1,2\n3,4"

    class FakeResponse:
        def raise_for_status(self): pass
        @property
        def content(self): return fake_content

    monkeypatch.setattr("requests.get", lambda u: FakeResponse())
    download_file(url, output_path)
    assert os.path.exists(output_path)
    with open(output_path, "rb") as f:
        assert f.read() == fake_content

def test_extract_csv_from_zip_creates_dir_and_extracts(temp_dir):
    # Cria um zip com dois CSVs e um TXT
    zip_path = os.path.join(temp_dir, "test.zip")
    csv1 = "a.csv"
    csv2 = "b.csv"
    txt = "c.txt"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr(csv1, "col1\n1")
        z.writestr(csv2, "col2\n2")
        z.writestr(txt, "not a csv")
    extract_dir = os.path.join(temp_dir, "data", "test")
    os.makedirs(extract_dir, exist_ok=True)
    csv_files = extract_csv_from_zip(zip_path, extract_dir)
    assert os.path.isdir(extract_dir)
    assert sorted([os.path.basename(f) for f in csv_files]) == sorted([csv1, csv2])
    assert all(f.endswith(".csv") for f in csv_files)
    assert not os.path.exists(zip_path)
    for f in csv_files:
        assert os.path.exists(f)

def test_extract_csv_from_zip_no_csv(temp_dir):
    zip_path = os.path.join(temp_dir, "no_csv.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("file.txt", "not a csv")
    extract_dir = os.path.join(temp_dir, "data", "no_csv")
    os.makedirs(extract_dir, exist_ok=True)
    csv_files = extract_csv_from_zip(zip_path, extract_dir)
    assert csv_files == []
    assert not os.path.exists(zip_path)