import wandb
import mlflow
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)

def log_artifact(nome_artefato, tipo_artefato, descricao_artefato, nome_arquivo, execucao_wandb):
    """
    Registra um artefato no Weights & Biases.

    Parâmetros
    ----------
    nome_artefato : str
        O nome do artefato.
    tipo_artefato : str
        O tipo do artefato.
    descricao_artefato : str
        Uma breve descrição do artefato.
    nome_arquivo : str
        O caminho para o arquivo a ser carregado como um artefato.
    execucao_wandb : wandb.Run
        A execução do Weights & Biases para registrar o artefato.

    Retorna
    -------
    Nada
    """
    
    artefato = wandb.Artifact(
        nome_artefato,
        type=tipo_artefato,
        description=descricao_artefato,
    )
    artefato.add_file(nome_arquivo)
    execucao_wandb.log_artifact(artefato)
    #artefato.wait() # Mantido comentado, pois estava comentado no original
    logger.info(f"Artefato {nome_artefato} registrado no W&B.")
