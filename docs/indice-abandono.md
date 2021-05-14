# Painel Vacina - Especificação

# Índice

1. [Módulo de Processamento dos Dados](#Módulo-de-Processamento-dos-Dados)
2. [Módulo de Visualização dos Dados](#Módulo-de-Visualização-dos-Dados)

# Módulo de Processamento dos Dados

O módulo de processamento é implementado pelo _script_ `data_processing.py` que recebe como único argumento o caminho da tabela tratada gerada no módulo anterior:

```console
$ python processing.py "caminho/para/tabela.csv"
```

Para cada __item de visualização__ o script implementa métodos que processam os dados de forma independente e ao final do processo, geram tabelas no formato _.csv_ na estrutra de diretórios especificada anteriormente. A seguir, detalhamos a especificação do processamento de dados do item "Índice de abandono vacinal".

### Índice de abandono vacinal

* Objetivo:
    * Calcular o índice de abandono vacinal atual da campanha de vacinação no grupo selecionado. O índice de abandono vacinal da campanha de vacinação é dado pela porporção de pessoas que iniciam o esquema vacinal, porém não o conclui.
* Entrada:
    * Tabela tratada com apenas as seguintes colunas mantidas:
        * ID_PACIENTE
        * DATA_APLICAÇÃO
        * NOME_VACINA
        * DOSE_VACINA
        * UF
        * MUNICIPIO
    * Para cada tipo de vacina, o prazo máximo em dias em que ela deve ser aplicada.
* SAÍDA:
    * Para cada par (UF, MUNICIPIO), isto é, cada diretório no __nível municipal__, gerar uma arquivo com nome `indice-abandono.csv` com a seguinte estrutura:
    * Uma coluna com nome __Data__ onde o único valor é uma _string_ no formato __YYYY-MM-DD__, representando a data mais recente em DATA_APLICAÇÃO.
    * As demais colunas são obtidas através dos nomes únicos em NOME_VACINA.
    * A tabela possuirá uma única linha indicando para o dia em __Data__ o valor do índice de abandono para cada tipo de vacina.

Como exemplo, se a entrada for a tabela a seguir (suponha que o prazo máximo para A seja de 3 dias e para B seja de 2 dias):

| DATA_APLICAÇÃO | PACIENTE_ID | NOME_VACINA | DOSE_VACINA |  UF | MUNICIPIO |
|:--------------:|:-----------:|:-----------:|:-----------:|:---:|:---------:|
|   2021-01-01   |      1      |      A      |      1      |  X  |     Y     |
|   2021-01-01   |      2      |      A      |      1      |  X  |     Y     |
|   2021-01-01   |      3      |      B      |      1      |  X  |     Y     |
|   2021-01-04   |      1      |      A      |      1      |  X  |     Y     |
|   2021-01-04   |      3      |      B      |      2      |  X  |     Y     |
|   2021-01-05   |      4      |      A      |      1      |  X  |     Y     |
|   2021-01-05   |      5      |      A      |      2      |  X  |     Y     |

A saída deverá ser a seguinte tabela:

|    Data    |   A   |   B   |
|:----------:|:-----:|:-----:|
| 2021-01-05 |  .50  |  .00  |

#### Implementação do algoritmo

Para calcular o índice, determinamos o valor da data de aplicação mais recente (`data_maxima`) e para cada tipo de vacina determinamos o grupo _F_ de pessoas que tomaram a primeira dose até `data_maxima` - `prazo_maximo(NOME_VACINA)`. No exemplo anterior, para a vacina A temos F = {1, 2} (o grupo está representado pelo PACIENTE_ID). Em seguida calculamos o grupo S de pessoas que estão em F e tomaram a segunda dose até `data_maxima`. No exemplo anterior S = {1}. A taxa de abandono será dada por (|F| - |S|) / |F|. Para as outras colunas o procedimento é análogo.

# Módulo de Visualização dos Dados

O módulo de visualização é implementado pelo _script_ `data_visualization.py` que recebe como argumentos o nome do arquivo que identifica o item a ser visualizado, a unidade federativa e o município a que os dados se referem.

Exemplo:
```console
$ python data_visualization.py doses-aplicadas-por-dia AL MACEIO
```
A seguir, detalhamos a especificação da geração dos dados de visualização do item "Índice de abandono vacinal".

### Doses aplicadas por dia

* Objetivo:
    * Visualizar o índice de abandono vacinal atual da campanha de vacinação no grupo selecionado, seprando por tipo de vacina. A componente de visualização gerada, será um simples gráfico de barras gerado a partir da tabela `indice-abandono.csv`
* Entrada:
    * Tabela processada encontrada em (por exemplo):
        * datasets/AL/MACEIO/indice-abandono.csv
* SAÍDA:
    * Objeto representando a figura, de acordo com a especificação do objetivo.