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

### Demanda de 2ªs doses por dia
* Objetvo:
    * Calcular o número de segundas doses necessárias nos próximos dias, por tipo de vacina.
* Entrada:
    * Tabela tratada de cada região (Brasil, UF ou Município) com as seguintes colunas:
        * vacina_dataAplicacao
        * vacina_descricao_dose
        * paciente_id
        * vacina_nome

* SAÍDA:
    * Para cada par (UF, MUNICIPIO), isto é, cada diretório no __nível municipal__, gerar uma arquivo com nome `demanda-vacinal.csv` com a seguinte estrutura:
    * Uma coluna com nome __Data__ onde cada valor é uma _string_ no formato __YYYY-MM-DD__.
    * Uma coluna com o nome __Vacina__ onde cada valor é uma _string_ que representa uma vacina distinta.
    * Uma coluna com o nome __Quantidade__ onde cada valor é um _int_ que representa a quantidade de demanda por segundas doses.
    * A quantidade de linhas da tabela deve equivaler a (__número de vacinas distintas__) * (__tamanho da janela de dias que contemple todas as futuras demandas__)

Como exemplo, se a entrada for a tabela a seguir:

| vacina_dataAplicacao | vacina_descricao_dose | paciente_id | vacina_nome |  UF | MUNICIPIO |
|:--------------------:|:---------------------:|:-----------:|:-----------:|:---:|:---------:|
|      2021-01-01      |         1ª            |      x      |   pfizer    |  X  |     Y     |
|      2021-01-01      |         1ª            |      y      | astrazeneca |  X  |     Y     |
|      2021-01-01      |         1ª            |      z      |  coronavac  |  X  |     Y     |

A saída deverá ser a seguinte tabela:

|    Data    |  Vacina   | Quantidade |
|:----------:|:---------:|:----------:|
| 2021-03-26 |  pfizer   |      1     |
| 2021-01-29 |astrazeneca|      1     |
| 2021-01-26 | coronavac |      1     |

#### Implementação do algoritmo

Basta criar uma nova coluna no dataset, DataSegundaDose, somando a quantidade máxima de dias para a aplicação da segunda dose. Depois, agrupando o drataframe por DataSegundaDose e vacina_nome, respectivamente, basta pegar a contagem desses dados, colocar numa coluna chamada Quantidade e o dataframe estará pronto.

# Módulo de Visualização dos Dados

O módulo de visualização é implementado pelo _script_ `data_visualization.py` que recebe como argumentos o nome do arquivo que identifica o item a ser visualizado, a unidade federativa e o município a que os dados se referem.

Exemplo:
```console
$ python data_visualization.py doses-aplicadas-por-dia AL MACEIO
```
A seguir, detalhamos a especificação da geração dos dados de visualização do item "Doses Aplicadas por dia".

### Doses aplicadas por dia

* Objetivo:
    * Visualizar o número total da demanda por segundas doses de vacina por dia e por tipo de vacina.
* Entrada:
    * Tabela processada encontrada em:
        * datasets/AL/MACEIO/demanda-vacinal.csv
* SAÍDA:
    * Objeto representando a figura, de acordo com a especificação do objetivo.

#### Implementação do algoritmo

Basta carregar o dataframe da região escolhida, o eixo x será as datas, o eixo y será as quantidades e a cor será o tipo de vacina.