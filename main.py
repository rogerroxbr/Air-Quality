import os
import wandb
import tempfile
import hydra
import mlflow
import logging
from omegaconf import DictConfig
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

_steps = [
    "download"
]

@hydra.main(config_name="config", config_path=".", version_base="1.1")
def go(config: DictConfig):
    # Carrega as variáveis do arquivo .env
    load_dotenv()

    # Setup the wandb experiment. All runs will be grouped under this name
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    # Login to wandb usando a chave do .env
    login_result = wandb.login(key=os.getenv("WANDB_API_KEY"))
    if login_result:
        logging.info("Login no Weights & Biases realizado com sucesso.")
    else:
        logging.info("Falha ao realizar login no Weights & Biases.")

    # Steps to execute
    steps_par = config["main"]["steps"]
    active_steps = steps_par.split(",") if steps_par != "all" else _steps

    # Move to a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        if "download" in active_steps:
            # Download the file
            _ = mlflow.run(
                f"{config['main']['components_repository']}/get_data",
                "main",
                parameters={
                    "sample": config["etl"]["sample"],
                    "artifact_name": "AirQuality.csv",
                    "artifact_type": "raw_data",
                    "artifact_description": config["etl"]["artifact_description"]   
                },
                env_manager="local",
            )

if __name__ == "__main__":
    go()