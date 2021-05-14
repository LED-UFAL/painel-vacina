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

### Doses aplicadas, ritmo de vacinação para primeiras e segundas doses, e fim da vacinação

* Objetivo:
    * Calcular o total de doses aplicadas, total de primeiras doses aplicadas, total de segundas doses aplicadas, ritmo de vacinação de primeiras e segundas doses, em doses/dia, e quantos dias faltam para o fim da vacinação.
* Entrada:
    * Tabela das vacinas tratada com apenas as seguintes colunas mantidas:
        * DATA_APLICAÇÃO
        * DOSE_VACINA
        * UF
        * MUNICIPIO

    * Tabela secundária com os municípios e o tamanho da população de cada município, com as seguintes tabelas:
        * UF
        * MUNICIPIO
        * POPULACAO

* SAÍDA:
    * Para cada par (UF, MUNICIPIO), isto é, cada diretório no __nível municipal__, gerar uma arquivo com nome `indicadores.csv` com a seguinte estrutura:
    * Uma coluna com nome __total_doses__ onde cada valor é um _int_, representando o total de doses aplicadas.
    * Uma coluna com nome __1as_doses__ onde cada valor é um _int_, representando o total de primeiras doses aplicadas.
    * Uma coluna com nome __2as_doses__ onde cada valor é um _int_, representando o total de segundas doses aplicadas.
    * Uma coluna com nome __ritmo_1as__ onde cada valor é um _int_, representando a velocidade de vacinação com primeiras doses nos últimos 30 dias (usa a função teto no float resultante do cálculo), em doses/dia.
    * Uma coluna com nome __ritmo_2as__ onde cada valor é um _int_, representando a velocidade de vacinação com segundas doses nos últimos 30 dias (usa a função teto no float resultante do cálculo), em doses/dia.
    * Uma coluna com nome __fim_vacinacao__ onde cada valor é um _int_, representando a quantidade de dias necessários para o fim da vacinação.
    * A quantidade de linhas da tabela é sempre igual a 1.

Como exemplo, se a entrada for a tabela das vacinas a seguir:

| DATA_APLICAÇÃO | NOME_VACINA | DOSE_VACINA |  UF | MUNICIPIO |
|:--------------:|:-----------:|:-----------:|:---:|:---------:|
|   2021-05-01   |      A      |      1      |  X  |     Y     |
|   2021-05-01   |      B      |      1      |  X  |     Y     |
|   2021-05-05   |      A      |      2      |  X  |     Y     |

Tabela secundária:

|    UF     | MUNICIPIO | POPULACAO |
|:---------:|:---------:|:---------:|
|     X     |     Y     |     Z     |

A saída deverá ser a seguinte tabela:

| total_doses | 1as_doses | 2as_doses | ritmo_1as | ritmo_2as | fim_vacinacao |
|:-----------:|:---------:|:---------:|:---------:|:---------:|:-------------:|
|      3      |     2     |     1     |     1     |     1     |  Z/ritmo_2as  |

#### Implementação do algoritmo

Basta contar a quantidade de doses, depois filtrar pelo tipo da dose e contar a quantidade de primeiras doses, contar a quantidade de segundas doses. Depois, filtramos as doses aplicadas nos últimos 30 dias e contamos, respectivamente, as primeiras e segundas doses. Essa quantidade contada será dividida por 30 e, depois de aplicar a função teto, serão, respectivamente, os ritmos de vacinação para a primeira e segunda dose. O fim da vacinação se dará pelo quociente da quantidade de população (obtida pela tabela secundária) na região dividido pelo ritmo de vacinação para as segundas doses.

# Módulo de Visualização dos Dados

O módulo de visualização é implementado pelo _script_ `data_visualization.py` que recebe como argumentos o nome do arquivo que identifica o item a ser visualizado, a unidade federativa e o município a que os dados se referem.

Exemplo:
```console
$ python data_visualization.py indicadores AL MACEIO
```
A seguir, detalhamos a especificação da geração dos dados de visualização do item "Doses Aplicadas por dia".

### Doses aplicadas, ritmo de vacinação para primeiras e segundas doses, e fim da vacinação

* Objetivo:
    * Visualizar o número total de doses aplicadas, o número total de primeiras doses aplicadas, o número total de segundas doses aplicadas, o ritmo de aplicação de primeiras doses, o ritmo de aplicação de segundas doses e o fim da vacinação, para cada _UF_ e _MUNICIPIO_ escolhidos nos dropdowns.
* Entrada:
    * Tabela processada encontrada em:
        * datasets/AL/MACEIO/indicadores.csv
    * Duas tring, representando o UF e o MUNICIPIO escolhido para ser feita a visualização dos indicadores.
* SAÍDA:
    * Dados numéricos, extraidos do datasets/AL/MACEIO/indicadores.csv.

#### Implementação do algoritmo

Basta apenas ler o arquivo datasets/AL/MACEIO/indicadores.csv e retornar os indicadores, que estarão na primeira e única linha.