import os
import logging
import requests
import zipfile
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)

def download_file(url, output_path):
    logger.info(f"Baixando arquivo de {url} para {output_path}")
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    logger.info("Download concluído.")

def extract_csv_from_zip(zip_path, extract_dir=None):
    """
    Extrai arquivos CSV de um zip para o diretório especificado.
    Se extract_dir não for informado, extrai para 'data/<nome_do_zip_sem_extensão>' no root do projeto.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    data_root = os.path.join(project_root, 'data')
    base_name = os.path.splitext(os.path.basename(zip_path))[0]
    if extract_dir is None:
        extract_dir = os.path.join(data_root, base_name)
    logger.info(f"Extraindo arquivos CSV de {zip_path} para {extract_dir}")
    os.makedirs(extract_dir, exist_ok=True)
    csv_files = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.csv'):
                zip_ref.extract(file, extract_dir)
                csv_files.append(os.path.join(extract_dir, file))
    if not csv_files:
        logger.warning("Nenhum arquivo CSV encontrado no zip.")
    else:
        logger.info(f"Arquivos CSV extraídos: {csv_files}")
    try:
        os.remove(zip_path)
        logger.info(f"Arquivo zip deletado: {zip_path}")
    except Exception as e:
        logger.warning(f"Não foi possível deletar o arquivo zip: {e}")
    return csv_files

def artifact_exists(project, artifact_name):
    api = wandb.Api()
    try:
        s = api.artifact(f"{project}/{artifact_name}")
        print (s)
        return True
    except wandb.errors.CommError:
        return False
    except wandb.errors.Error:
        return False