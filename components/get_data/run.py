#!/usr/bin/env python
import argparse
import os
import logging
import wandb
import sys
from wandb_utils.utils import download_file, extract_csv_from_zip, artifact_exists
from wandb_utils.log_artifact import log_artifact

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)

print("Argumentos do sistema:", sys.argv)
def go(args):
    # Usa o diretório de dados local fornecido por argumento
    logger.info(f"Usando diretório de dados local: {args.local_data_dir}")
    os.makedirs(args.local_data_dir, exist_ok=True)
    
    project = os.environ.get("WANDB_PROJECT")
    # Mantido artifact_full_name por clareza, já que é um nome composto
    artifact_full_name = args.artifact_name

    if project and artifact_exists(project, artifact_full_name):
        logger.info(f"Artefato '{artifact_full_name}' encontrado no W&B. Baixando diretamente do W&B.")
        run = wandb.init(project=project, job_type="download_file")
        artifact = run.use_artifact(artifact_full_name)
        # Baixa para o diretório de dados local configurado
        artifact_dir = artifact.download(args.local_data_dir)
        logger.info(f"Arquivo {artifact_full_name} baixado para a pasta '{args.local_data_dir}'")
        csv_files = [os.path.join(artifact_dir, f) for f in os.listdir(artifact_dir) if f.endswith(".csv")]
        if not csv_files:
            logger.error("Nenhum arquivo CSV encontrado no artefato do W&B.")
            return
        file_to_log = csv_files[0] # Mantido file_to_log por clareza
        run.finish()
    else:
        logger.info(f"Artefato '{artifact_full_name}' não encontrado no W&B. Baixando do link fornecido.")
        # Usa o diretório de dados local para o caminho de saída
        output_path = os.path.join(args.local_data_dir, os.path.basename(args.sample))
        download_successful = download_file(args.sample, output_path)

        if not download_successful:
            logger.error(f"Falha ao baixar o arquivo de {args.sample}. Verifique a URL e a conexão de rede. Interrompendo o processo.")
            return

        if output_path.endswith(".zip"):
            # Extrai para o diretório de dados local configurado
            csv_files = extract_csv_from_zip(output_path, extract_dir=args.local_data_dir, delete_zip_after_extraction=True)
            if not csv_files:
                logger.error("Nenhum arquivo CSV encontrado para enviar ao W&B.")
                return
            file_to_log = csv_files[0]
        elif output_path.endswith(".csv"):
            file_to_log = output_path
        else:
            logger.error("O arquivo baixado não é .zip nem .csv. Nada será enviado ao W&B.")
            return

        run = wandb.init(job_type="download_file")
        run.config.update(vars(args)) # vars(args) é idiomático, mantido

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
    import argparse
    # Mantido parser por ser convenção
    parser = argparse.ArgumentParser(description="Baixa uma URL para um destino local e envia o CSV para o W&B")
    parser.add_argument("--sample", type=str, help="URL da amostra para baixar")
    parser.add_argument("--artifact_name", type=str, help="Nome do artefato no W&B (padrão: nome do arquivo baixado)")
    parser.add_argument("--artifact_type", type=str, help="Tipo do artefato (padrão: raw_data)")
    parser.add_argument("--artifact_description", type=str, help="Descrição do artefato (padrão: Dados brutos)")
    # Novo argumento para o diretório de dados local
    parser.add_argument(
        "--local_data_dir", 
        type=str, 
        default="data", 
        help="Diretório local para baixar e extrair arquivos (padrão: data)"
    )
    args = parser.parse_args() # Mantido args por ser convenção
    print("Argumentos:", args)
    go(args)
