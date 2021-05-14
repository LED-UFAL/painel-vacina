# Painel Vacina - Especificação

# Índice

1. [Descrição do Problema](#Descrição-do-Problema)
2. [Estrutura dos Projeto](#Estrutura-do-Projeto)
2. [Módulo de Processamento dos Dados](#Módulo-de-Processamento-dos-Dados)
3. [Módulo de Visualização dos Dados](#Módulo-de-Visualização-dos-Dados)

# Descrição do Problema

O objetivo desse documento é a especificar o funcionamento e estrutra dos dois módulos (processamento e visualização de dados) do painel interativo sobre os dados de vacinação provenientes da base aberta de dados do [openDataSus](https://opendatasus.saude.gov.br/dataset/covid-19-vacinacao).

# Estrutura do Projeto

A estrutra básica do projeto consiste em implementar três módulos fundamentais:

1. Módulo de __tratamento dos dados__ - responsável por ler os dados brutos disponibilizados pelo `openDataSus` e tratá-los, gerando ao final do processo uma tabela _uniformizada_. Além disso o módulo deve gerar um relatório descrevendo quais anomalias foram encontradas durante o processo de tratamento e qual ação foi tomada para resolver o problema.

2. Módulo de __processamento dos dados__ - responsável por ler a tabela uniformizada pelo módulo de tratamento e processar/transformar os dados que serão utilizados pelo módulo seguinte (de visualização) para gerar os elementos visuais do painel (gráficos de séries temporais, indicadores etc).

3. Módulo de __visualização dos dados__ - responsável por ler os dados gerados pelo módulo de processamento e gerar os elementos visuais sem aplicar __nenhuma__ modificação.

A estrutra final do projeto deverá seguir a seguinte hirearquia de diretórios:

```
painel-vacina
    datasets
        BRASIL <------------ Nível estadual
            TODOS <-------- Nível municipal
                item1.csv
                item2.csv
        AL
            ARAPIRACA
                item1.csv
                item2.csv
            MACEIO
                item1.csv
                item2.csv
            .
            .
        .
        .
    # modulo
        treatment.py
        processing.py
        visualization.py
    app.py
```

# Módulo de Processamento dos Dados

O módulo de processamento é implementado pelo _script_ `data_processing.py` que recebe como único argumento o caminho da tabela tratada gerada no módulo anterior:

```console
$ python processing.py "caminho/para/tabela.csv"
```

Para cada __item de visualização__ o script implementa métodos que processam os dados de forma independente e ao final do processo, geram tabelas no formato _.csv_ na estrutra de diretórios especificada anteriormente. A seguir, detalhamos a especificação do processamento de dados do item "Doses Aplicadas por dia".

### Doses aplicadas por dia

* Objetivo:
    * Calcular o número total de doses aplicadas nos últimos dias por tipo de vacina e por tipo de dose.
* Entrada:
    * Tabela tratada com apenas as seguintes colunas mantidas:
        * DATA_APLICAÇÃO
        * NOME_VACINA
        * DOSE_VACINA
        * UF
        * MUNICIPIO
* SAÍDA:
    * Para cada par (UF, MUNICIPIO), isto é, cada diretório no __nível municipal__, gerar uma arquivo com nome `doses-aplicadas-por-dia.csv` com a seguinte estrutura:
    * Uma coluna com nome __Data__ onde cada valor é uma _string_ no formato __YYYY-MM-DD__.
    * As demais colunas são geradas através da combinação de todos os nomes únicos em NOME_VACINA e DOSE_VACINA __nesta ordem__.
    * Adicionalmente, duas colunas são geradas contendo as quantidades agregados por tipo de dose (sem discriminar o nome da vacina).
    * A quantidade de linhas da tabela deve equivaler ao período em dias entre a __menor data__ e __maior data__ em DATA_APLICAÇÃO.

Como exemplo, se a entrada for a tabela a seguir:

| DATA_APLICAÇÃO | NOME_VACINA | DOSE_VACINA |  UF | MUNICIPIO |
|:--------------:|:-----------:|:-----------:|:---:|:---------:|
|   2021-01-01   |      A      |      1      |  X  |     Y     |
|   2021-01-01   |      B      |      1      |  X  |     Y     |
|   2021-01-05   |      A      |      2      |  X  |     Y     |

A saída deverá ser a seguinte tabela:

|    Data    | A-1 | A-2 | B-1 |  Todos-1  |  Todos-2  |
|:----------:|:---:|:---:|:---:|:---------:|:---------:|
| 2021-01-01 |  1  |  0  |  1  |     2     |     0     |
| 2021-01-02 |  0  |  0  |  0  |     0     |     0     |
| 2021-02-03 |  0  |  0  |  0  |     0     |     0     |
| 2021-01-04 |  0  |  0  |  0  |     0     |     0     |
| 2021-01-05 |  0  |  1  |  0  |     0     |     1     |

#### Implementação do algoritmo

A implementação é trivial, bastando indexar a tabela resultante (inicialmente zerada) pelos valores da data e, para cada registro na tabela de entrada, incrementar o valor em 1 nas células [DATA_APLICAÇÃO, NOME_VACINA-DOSE_VACINA] e [DATA_APLICAÇÃO, DOSE_VACINA].

### Total de doses aplicadas

* Objetivo:
    * Calcular o número total de doses aplicadas nos últimos dias por tipo de vacina e por tipo de dose.
* Entrada:
    * Tabela Processada no passo anterior: `doses-aplicadas-por-dia.csv`.
* SAÍDA:
    * Para cada par (UF, MUNICIPIO), isto é, cada diretório no __nível municipal__, gerar uma arquivo com nome `total-doses-aplicadas-por-dia.csv` com a seguinte estrutura:
    * Uma coluna com nome __Data__ onde o único valor é uma _string_ no formato __YYYY-MM-DD__, representando a data mais recente em DATA_APLICAÇÃO.
    * Colunas "Total de Doses Aplicadas", "Total de Primeiras Doses Aplicadas", "Total de Segundas Doses Aplicadas"

Como exemplo, se a entrada for a tabela a seguir:

|    Data    | A-1 | A-2 | B-1 |  Todos-1  |  Todos-2  |
|:----------:|:---:|:---:|:---:|:---------:|:---------:|
| 2021-01-01 |  1  |  0  |  1  |     2     |     0     |
| 2021-01-02 |  0  |  0  |  0  |     0     |     0     |
| 2021-02-03 |  0  |  0  |  0  |     0     |     0     |
| 2021-01-04 |  0  |  0  |  0  |     0     |     0     |
| 2021-01-05 |  0  |  1  |  0  |     0     |     1     |

A saída será:

|    Data    | Total de Doses Aplicadas | Total de Primeiras Doses Aplicadas | Total de Segundas Doses Aplicadas |
|:----------:|:------------------------:|:----------------------------------:|:---------------------------------:|
| 2021-01-05 |           3              |                  2                 |                  1                |

#### Implementação do algoritmo

A implementação é trivial, bastando acumular os valores em Todos-1 e Todos-2 da tabela `doses-aplicadas-por-dia.csv`. Para o total de doses, o valor acumulado é obtido sobre a soma das colunas Todos-1 + Todos-2.

# Módulo de Visualização dos Dados

O módulo de visualização é implementado pelo _script_ `data_visualization.py` que recebe como argumentos o nome do arquivo que identifica o item a ser visualizado, a unidade federativa e o município a que os dados se referem.

Exemplo:
```console
$ python data_visualization.py doses-aplicadas-por-dia AL MACEIO
```
A seguir, detalhamos a especificação da geração dos dados de visualização do item "Doses Aplicadas por dia".

### Doses aplicadas por dia

* Objetivo:
    * Visualizar o número total de doses aplicadas nos últimos dias por tipo de vacina e por tipo de dose. As cores devem representar o tipo de dose e deve existir um _dropdown_ para cada tipo de vacina a ser mostrado.
* Entrada:
    * Tabela processada encontrada em:
        * datasets/AL/MACEIO/doses-aplicadas-por-dia.csv
    * String, representando o nome da vacina (no exemplo anterior A ou B) ou string "Todos" (caso o gráfico deva mostrar os valores acumulados para todas as vacinas.)
* SAÍDA:
    * Objeto representando a figura, de acordo com a especificação do objetivo.

#### Implementação do algoritmo

Na abordagem com o parâmetro para o nome da vacina, o módulo de visualização realiza um pequeno processamento da tabela, selecionando colunas que contém o nome de vacina passado.

### Total de doses aplicadas

* Objetivo:
    * Visualizar o número total de doses aplicadas por tipo de vacina e por tipo de dose. Os indicadores serão simplesmente exibidos na tela do painel (sem nenhuma componente visual específica associada).
* Entrada:
    * Tabela processada encontrada em:
        * datasets/AL/MACEIO/total-doses-aplicadas-por-dia.csv
* SAÍDA:
    * Componente HTML (texto) com os indicadores representando as números calculados, de acordo com a especificação do objetivo.