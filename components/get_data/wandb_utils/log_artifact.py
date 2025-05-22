import wandb
import mlflow
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)

def log_artifact(artifact_name, artifact_type, artifact_description, filename, wandb_run):
    """
    Log an artifact to Weights & Biases.

    Parameters
    ----------
    artifact_name : str
        The name of the artifact.
    artifact_type : str
        The type of the artifact.
    artifact_description : str
        A brief description of the artifact.
    filename : str
        The path to the file to be uploaded as an artifact.
    wandb_run : wandb.Run
        The Weights & Biases run to log the artifact to.

    Returns
    -------
    None
    """
    
    artifact = wandb.Artifact(
        artifact_name,
        type=artifact_type,
        description=artifact_description,
    )
    artifact.add_file(filename)
    wandb_run.log_artifact(artifact)
    #artifact.wait()
    logger.info(f"Artifact {artifact_name} logged to W&B.")
