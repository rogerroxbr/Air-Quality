# Air-Quality

Análise exploratória de dados (EDA) sobre qualidade do ar, utilizando conjuntos de dados públicos de diferentes regiões e períodos. O objetivo é entender padrões, tendências e fatores que afetam a qualidade do ar, além de fornecer visualizações e insights relevantes.

## Estrutura do Projeto

- `main.py`: Script principal para execução de análises e processamento de dados.
- `Data/`: Conjuntos de dados utilizados.
  - `air+quality/`: Dados do Air Quality UCI.
  - `PRSA2017_Data_20130301-20170228/`: Dados de qualidade do ar de Pequim (multi-site).
- `EDA/`: Notebooks de análise exploratória.
  - `Air quality EDA.ipynb`: EDA dos dados do Air Quality UCI.
  - `Beijing Multi-Site Air Quality.ipynb`: EDA dos dados de Pequim.
- `pyproject.toml`: Gerenciamento de dependências e configuração do ambiente.

## Instalação

1. Clone o repositório:
   ```sh
   git clone https://github.com/seu-usuario/air-quality.git
   cd air-quality
   ```

2. (Opcional) Crie um ambiente virtual:
   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
   ou, se preferir:
   ```sh
   pip install .
   ```

   **Ou utilizando [uv](https://github.com/astral-sh/uv) para instalação mais rápida:**
   ```sh
   uv pip install -r requirements.txt
   ```
   ou:
   ```sh
   uv pip install .
   ```

## Como usar

- Execute os notebooks em `EDA/` para explorar e visualizar os dados.
- Utilize o `main.py` para análises automatizadas ou processamento adicional.

## Principais Bibliotecas Utilizadas

- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn

## Sobre os Dados

Os dados utilizados estão disponíveis nas pastas dentro de `Data/`. Certifique-se de manter a estrutura de diretórios para garantir o funcionamento dos notebooks e scripts.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.