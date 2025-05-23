import os
import types
import pytest

import components.get_data.run as run

class DummyWandbRun:
    def __init__(self):
        self.logged_artifacts = []
        self.config = types.SimpleNamespace()
        self.config.update = lambda d: None
        self.finished = False
    def log_artifact(self, artifact):
        self.logged_artifacts.append(artifact)
    def finish(self):
        self.finished = True

class DummyArtifact:
    def __init__(self, name, type, description):
        self.name = name
        self.type = type
        self.description = description
        self.files = []
    def add_file(self, file_path):
        self.files.append(file_path)
    def wait(self):
        pass

@pytest.fixture
def dummy_wandb(monkeypatch):
    dummy_run = DummyWandbRun()
    dummy_api = type("DummyApi", (), {"artifact": lambda self, name: True})()
    monkeypatch.setattr(run.wandb, "init", lambda *a, **kw: dummy_run)
    monkeypatch.setattr(run.wandb, "Artifact", lambda n, type, description: DummyArtifact(n, type, description))
    monkeypatch.setattr(run.wandb, "Api", lambda: dummy_api)
    return dummy_run

@pytest.fixture
def dummy_utils(monkeypatch, tmp_path):
    # Mock download_file
    def fake_download_file(url, output_path):
        with open(output_path, "w") as f:
            f.write("col1,col2\n1,2\n")
    # Mock extract_csv_from_zip
    def fake_extract_csv_from_zip(zip_path, extract_dir=None):
        if extract_dir is None:
            extract_dir = ".data"
        csv_path = os.path.join(extract_dir, "file.csv")
        os.makedirs(extract_dir, exist_ok=True)
        with open(csv_path, "w") as f:
            f.write("col1,col2\n1,2\n")
        return [csv_path]
    # Mock log_artifact
    def fake_log_artifact(name, type, desc, filename, wandb_run):
        artifact = DummyArtifact(name, type, desc)
        artifact.add_file(filename)
        wandb_run.log_artifact(artifact)
    # Mock artifact_exists
    def fake_artifact_exists(project, artifact_name):
        return False
    monkeypatch.setattr(run, "download_file", fake_download_file)
    monkeypatch.setattr(run, "extract_csv_from_zip", fake_extract_csv_from_zip)
    monkeypatch.setattr(run, "log_artifact", fake_log_artifact)
    monkeypatch.setattr(run, "artifact_exists", fake_artifact_exists)

def make_args(sample, artifact_name="test_art", artifact_type="dataset", artifact_description="desc"):
    class Args:
        pass
    args = Args()
    args.sample = sample
    args.artifact_name = artifact_name
    args.artifact_type = artifact_type
    args.artifact_description = artifact_description
    return args

def test_go_with_csv(tmp_path, dummy_wandb, dummy_utils):
    csv_path = tmp_path / "file.csv"
    args = make_args(str(csv_path))
    with open(csv_path, "w") as f:
        f.write("col1,col2\n1,2\n")
    run.go(args)
    assert dummy_wandb.logged_artifacts
    artifact = dummy_wandb.logged_artifacts[0]
    expected_paths = [os.path.join("data", "file.csv"), os.path.join(".data", "file.csv")]
    assert artifact.files[0] in expected_paths
    assert artifact.name == "test_art"

def test_go_with_zip(tmp_path, dummy_wandb, dummy_utils):
    zip_path = tmp_path / "file.zip"
    args = make_args(str(zip_path))
    run.go(args)
    assert dummy_wandb.logged_artifacts
    artifact = dummy_wandb.logged_artifacts[0]
    assert artifact.files[0].endswith("file.csv")

def test_go_with_invalid_file(tmp_path, dummy_wandb, dummy_utils):
    invalid_path = tmp_path / "file.txt"
    args = make_args(str(invalid_path))
    with open(invalid_path, "w") as f:
        f.write("not a csv or zip")
    run.go(args)
    # Nenhum artifact deve ser logado
    assert not dummy_wandb.logged_artifacts