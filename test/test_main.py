# test/test_main.py
import os
import pytest

import main

class DummyWandb:
    def __init__(self, login_result=True):
        self.login_result = login_result
        self.login_called = False
    def login(self, key=None):
        self.login_called = True
        return self.login_result

class DummyMlflow:
    def __init__(self):
        self.run_called = False
        self.run_args = None
    def run(self, *args, **kwargs):
        self.run_called = True
        self.run_args = (args, kwargs)
        return "dummy_run"

@pytest.fixture
def dummy_config():
    from omegaconf import OmegaConf
    return OmegaConf.create({
        "main": {
            "project_name": "air-quality",
            "experiment_name": "dev",
            "steps": "download",
            "components_repository": "https://github.com/rogerroxbr/Air-Quality#components"
        },
        "etl": {
            "sample": "https://archive.ics.uci.edu/static/public/360/air+quality.zip",
            "artifact_description": "Raw file as downloaded"
        }
    })

def test_pipeline_download_step(monkeypatch, dummy_config):
    dummy_wandb = DummyWandb(login_result=True)
    dummy_mlflow = DummyMlflow()
    monkeypatch.setattr(main, "wandb", dummy_wandb)
    monkeypatch.setattr(main, "mlflow", dummy_mlflow)
    monkeypatch.setattr(main, "load_dotenv", lambda: None)
    # Executa
    main.go(dummy_config)
    # Verifica login wandb
    assert dummy_wandb.login_called
    # Verifica chamada do mlflow.run
    assert dummy_mlflow.run_called
    args, kwargs = dummy_mlflow.run_args
    assert "get_data" in args[0]
    assert kwargs["parameters"]["sample"] == dummy_config["etl"]["sample"]
    assert kwargs["parameters"]["artifact_description"] == dummy_config["etl"]["artifact_description"]

def test_pipeline_wandb_login_fail(monkeypatch, dummy_config):
    dummy_wandb = DummyWandb(login_result=False)
    dummy_mlflow = DummyMlflow()
    monkeypatch.setattr(main, "wandb", dummy_wandb)
    monkeypatch.setattr(main, "mlflow", dummy_mlflow)
    monkeypatch.setattr(main, "load_dotenv", lambda: None)
    main.go(dummy_config)
    assert dummy_wandb.login_called
    assert dummy_mlflow.run_called

def test_pipeline_skip_download(monkeypatch, dummy_config):
    dummy_config["main"]["steps"] = "other_step"
    dummy_wandb = DummyWandb(login_result=True)
    dummy_mlflow = DummyMlflow()
    monkeypatch.setattr(main, "wandb", dummy_wandb)
    monkeypatch.setattr(main, "mlflow", dummy_mlflow)
    monkeypatch.setattr(main, "load_dotenv", lambda: None)
    main.go(dummy_config)
    # mlflow.run não deve ser chamado
    assert not dummy_mlflow.run_called