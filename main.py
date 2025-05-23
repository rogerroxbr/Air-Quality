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

    # Configura o experimento wandb. Todas as execuções serão agrupadas sob este nome
    # Tenta usar chaves traduzidas, com fallback para as originais.
    principal_config = config.get("principal", config["main"])
    etl_config = config.get("etl", config["etl"])
    paths_config = config.get("paths", {})

    os.environ["WANDB_PROJECT"] = principal_config.get("nome_projeto", config["main"]["project_name"])
    os.environ["WANDB_RUN_GROUP"] = principal_config.get("nome_experimento", config["main"]["experiment_name"])

    # Faz login no wandb usando a chave do .env
    login_result = wandb.login(key=os.getenv("WANDB_API_KEY"))
    if login_result:
        logging.info("Login no Weights & Biases realizado com sucesso.")
    else:
        logging.info("Falha ao realizar login no Weights & Biases.")

    # Passos a executar
    steps_par = principal_config.get("passos", config["main"]["steps"])
    active_steps = steps_par.split(",") if steps_par != "all" else _steps

    # Move para um diretório temporário
    with tempfile.TemporaryDirectory() as tmp_dir:
        if "download" in active_steps:
            # Parâmetros para o componente get_data
            # Tenta obter de chaves novas/traduzidas, com fallback para os valores antigos ou hardcoded.
            sample_url = etl_config.get("url_amostra", config["etl"]["sample"])
            # O artifact_name aqui é o que o main.py espera que o get_data produza.
            expected_artifact_name = etl_config.get("nome_artefato_gerado_pelo_get_data", "AirQuality.csv")
            expected_artifact_type = etl_config.get("tipo_artefato_gerado_pelo_get_data", "raw_data")
            # A descrição do artefato que get_data irá criar.
            artifact_description_for_get_data = etl_config.get("descricao_artefato_gerado_pelo_get_data", config["etl"]["artifact_description"])
            # Diretório local que get_data deve usar.
            local_data_dir_for_get_data = paths_config.get("diretorio_dados_local", "data")

            # Baixa o arquivo
            _ = mlflow.run(
                principal_config.get("repositorio_componentes", config['main']['components_repository']) + "/get_data",
                "main",
                parameters={
                    "sample": sample_url,
                    "artifact_name": expected_artifact_name, # Este é o nome do artefato que get_data irá criar
                    "artifact_type": expected_artifact_type,
                    "artifact_description": artifact_description_for_get_data,
                    "local_data_dir": local_data_dir_for_get_data # Novo parâmetro
                },
                env_manager="local",
            )

if __name__ == "__main__":
    go()