#!/usr/bin/env python
import argparse
import os
import logging
import wandb

from wandb_utils.utils import download_file, extract_csv_from_zip, artifact_exists
from wandb_utils.log_artifact import log_artifact

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)

def go(args):
    os.makedirs("data", exist_ok=True)
    project = os.environ.get("WANDB_PROJECT")
    artifact_full_name = args.artifact_name

    if project and artifact_exists(project, artifact_full_name):
        logger.info(f"Artifact '{artifact_full_name}' encontrado no W&B. Baixando direto do W&B.")
        run = wandb.init(project=project, job_type="download_file")
        artifact = run.use_artifact(artifact_full_name)
        artifact_dir = artifact.download("data")
        logger.info(f"Arquivo {artifact_full_name} baixado para data")
        csv_files = [os.path.join(artifact_dir, f) for f in os.listdir(artifact_dir) if f.endswith(".csv")]
        if not csv_files:
            logger.error("Nenhum arquivo CSV encontrado no artifact do W&B.")
            return
        file_to_log = csv_files[0]
        run.finish()
    else:
        logger.info(f"Artifact '{artifact_full_name}' não encontrado no W&B. Baixando do link fornecido.")
        output_path = os.path.join("data", os.path.basename(args.sample))
        download_file(args.sample, output_path)

        if output_path.endswith(".zip"):
            csv_files = extract_csv_from_zip(output_path, extract_dir="data")
            if not csv_files:
                logger.error("Nenhum arquivo CSV encontrado para enviar ao W&B.")
                return
            file_to_log = csv_files[0]
        elif output_path.endswith(".csv"):
            file_to_log = output_path
        else:
            logger.error("Arquivo baixado não é .zip nem .csv. Nada será enviado ao W&B.")
            return

        run = wandb.init(job_type="download_file")
        run.config.update(vars(args))

        logger.info(f"Enviando {args.artifact_name} para o Weights & Biases")
        log_artifact(
            args.artifact_name,
            args.artifact_type,
            args.artifact_description,
            file_to_log,
            run,
        )
        run.finish()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download URL to a local destination e envia o CSV para o W&B")
    parser.add_argument("sample", type=str, help="URL da base para download")
    parser.add_argument("--artifact_name", type=str,  help="Nome do artefato no wandb (padrão: teste)")
    parser.add_argument("--artifact_type", type=str, help="Tipo do artefato (padrão: teste)")
    parser.add_argument("--artifact_description", type=str, default="Arquivo CSV baixado", help="Descrição do artefato (padrão: teste)")
    args = parser.parse_args()
    go(args)