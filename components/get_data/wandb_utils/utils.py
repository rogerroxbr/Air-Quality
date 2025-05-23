import os
import logging
import requests
import zipfile
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)

def download_file(url, caminho_saida):
    """
    Baixa um arquivo de uma URL para um caminho de saída especificado.

    Parâmetros
    ----------
    url : str
        A URL do arquivo a ser baixado.
    caminho_saida : str
        O caminho local onde o arquivo será salvo.
    """
    logger.info(f"Baixando arquivo de {url} para {caminho_saida}")
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()  # Levanta um erro para respostas HTTP ruins (4xx ou 5xx)
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        with open(caminho_saida, "wb") as f:
            f.write(resposta.content)
        logger.info("Download concluído.")
        return True # Retorna True em caso de sucesso
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao baixar o arquivo de {url}: {e}")
        return False # Retorna False em caso de erro

def extract_csv_from_zip(caminho_zip, diretorio_extracao=None, delete_zip_after_extraction=True):
    """
    Extrai arquivos CSV de um arquivo .zip para o diretório especificado.
    Se diretorio_extracao não for informado, extrai para um subdiretório com o mesmo nome do arquivo .zip
    (sem a extensão .zip) localizado no mesmo diretório do arquivo .zip.
    Por exemplo, se caminho_zip é 'downloads/data.zip', o padrão para diretorio_extracao será 'downloads/data/'.

    Parâmetros
    ----------
    caminho_zip : str
        O caminho para o arquivo .zip.
    diretorio_extracao : str, opcional
        O diretório para onde os arquivos CSV serão extraídos. 
        Se None, o padrão é um subdiretório nomeado após o arquivo zip no mesmo diretório do zip.
    delete_zip_after_extraction : bool, opcional
        Se True, deleta o arquivo zip após a extração. O padrão é True.

    Retorna
    -------
    list
        Uma lista dos caminhos dos arquivos CSV extraídos, ou uma lista vazia se nenhum arquivo .csv for encontrado ou em caso de erro.
    """
    if not os.path.exists(caminho_zip):
        logger.error(f"Arquivo zip não encontrado em: {caminho_zip}")
        return []

    nome_base = os.path.splitext(os.path.basename(caminho_zip))[0]
    
    if diretorio_extracao is None:
        # Default: subdirectory in the same directory as the zip file
        diretorio_pai_zip = os.path.dirname(caminho_zip)
        # Se caminho_zip for apenas o nome do arquivo (sem diretório), diretorio_pai_zip será ''
        # os.path.join lidará com isso corretamente, criando o subdiretório no CWD.
        diretorio_extracao = os.path.join(diretorio_pai_zip, nome_base)

    logger.info(f"Extraindo arquivos CSV de '{caminho_zip}' para '{diretorio_extracao}'")
    
    try:
        os.makedirs(diretorio_extracao, exist_ok=True)
    except OSError as e:
        logger.error(f"Erro ao criar o diretório de extração '{diretorio_extracao}': {e}")
        return []

    arquivos_csv = []
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as ref_zip:
            for arquivo in ref_zip.namelist():
                if arquivo.endswith('.csv'):
                    # Assegurar que arquivos dentro de pastas no zip sejam extraídos corretamente
                    # e que o caminho final seja construído corretamente.
                    # O método extract já lida com a estrutura de pastas internas.
                    ref_zip.extract(arquivo, diretorio_extracao)
                    # O caminho do arquivo extraído será relativo a diretorio_extracao
                    caminho_completo_arquivo_extraido = os.path.join(diretorio_extracao, arquivo)
                    arquivos_csv.append(caminho_completo_arquivo_extraido)
        
        if not arquivos_csv:
            logger.warning(f"Nenhum arquivo .csv encontrado no arquivo zip: {caminho_zip}")
        else:
            logger.info(f"Arquivos CSV extraídos para '{diretorio_extracao}': {arquivos_csv}")

    except zipfile.BadZipFile:
        logger.error(f"Erro: O arquivo '{caminho_zip}' não é um arquivo zip válido ou está corrompido.")
        return [] # Retorna lista vazia em caso de erro de zip
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante a extração do zip '{caminho_zip}': {e}")
        return [] # Retorna lista vazia em caso de outros erros

    if delete_zip_after_extraction:
        try:
            os.remove(caminho_zip)
            logger.info(f"Arquivo zip '{caminho_zip}' deletado após extração.")
        except Exception as e:
            logger.warning(f"Não foi possível deletar o arquivo zip '{caminho_zip}' após extração: {e}")
    else:
        logger.info(f"Arquivo zip '{caminho_zip}' mantido após extração conforme solicitado (delete_zip_after_extraction=False).")
        
    return arquivos_csv

def artifact_exists(projeto, nome_artefato):
    """
    Verifica se um artefato existe no W&B.

    Parâmetros
    ----------
    projeto : str
        O nome do projeto no W&B.
    nome_artefato : str
        O nome do artefato.

    Retorna
    -------
    bool
        True se o artefato existir, False caso contrário.
    """
    api = wandb.Api()
    try:
        artefato_status = api.artifact(f"{projeto}/{nome_artefato}")
        logger.info(f"Artefato '{nome_artefato}' encontrado no projeto '{projeto}': {artefato_status}")
        return True
    except wandb.errors.CommError:
        logger.info(f"Artefato '{nome_artefato}' não encontrado no projeto '{projeto}' devido a erro de comunicação.")
        return False
    except wandb.errors.Error: # Captura genérica para outros erros do wandb
        logger.info(f"Artefato '{nome_artefato}' não encontrado no projeto '{projeto}'.")
        return False