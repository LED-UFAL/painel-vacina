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

### Atraso de vacinação
* Objetvo:
    * Calcular o número de pessoas que receberam a segunda dose depois do prazo, de acordo com os períodos máximos de cada vacina.
* Entrada:
    * Tabela tratada de cada região (Brasil, UF ou Município) com as seguintes colunas:
        * vacina_dataAplicacao
        * vacina_descricao_dose
        * paciente_id
        * vacina_nome

* SAÍDA:
    * Para cada par (UF, MUNICIPIO), isto é, cada diretório no __nível municipal__, gerar uma arquivo com nome `serie-atraso.csv` com a seguinte estrutura:
    * Uma coluna sem nome, onde cada valor é uma _string_ no formato __YYYY-MM-DD__.
    * Para cada nome de vacina, uma coluna nomeada com o nome da mesma, onde cada valor é um _float_ representando a quantidade de pessoas que estavam atrasadas e tomaram a segunda dose no dia correspondente à linha do valor.
    * A quantidade de linhas da tabela deve equivaler a janela: (__data de hoje__) - (__data da primeira 2ª dose registrada__).

Como exemplo, se a entrada for a tabela a seguir:

| vacina_dataAplicacao | vacina_descricao_dose | paciente_id | vacina_nome |
|:--------------------:|:---------------------:|:-----------:|:-----------:|
|      2021-02-01      |         1ª            |      x      |   pfizer    |
|      2021-02-01      |         1ª            |      y      | astrazeneca |
|      2021-02-01      |         1ª            |      z      |  coronavac  |

A saída deverá ser a uma tabela como a que segue:

|                | astrazeneca | coronavac | pfizer |
|:--------------:|:-----------:|:---------:|:------:|
|   2021-02-01   |     0.0     |    1.0    |  0.0   |
|   2021-02-02   |     0.0     |    0.0    |  0.0   |
|   2021-02-03   |     1.0     |    2.0    |  1.0   |

#### Implementação do algoritmo

Deve-se remodelar o dataset para usar _paciente\_id_ e _vacina\_nome__ como index, os valores de _vacina\_dose_ como colunas e os valores de _vacina\_dataAplicacao_ como valores dessas novas colunas. Após a transformação no dataset ele deve ser:

|                 |                 |   1ªDose   |   2ªDose   |
|:---------------:|:---------------:|:----------:|:----------:|
| __paciente_id__ | __vacina_nome__ |            |            |
|        x        |      pfizer     | 2020-02-03 | 2020-02-25 |
|        y        |   astrazeneca   | 2020-03-01 |     NaN    |
|        z        |    coronavac    | 2020-02-02 | 2020-02-21 |

Em seguida, são excluídos os valores nulos dessa nova tabela, _paciente\_id_ e _vacina\_nome_ são transformados em coluna novamente é criada uma nova coluna chamada _janela_ com o intervalo em dias entre a primeira e segunda dose de cada paciente. Após isso a tabela é limitada nas linhas onde a janela é maior que o prazo máximo da vacina em sua respectiva linha. Os dados restantes são agrupados pelos valores de _2ªDose_ e _vacina\_nome_, contando a quantidade de _paciente\_id_ em cada data. A nova tabela deve ser:

|            | vacina_nome | paciente_id |
|:----------:|:-----------:|:-----------:|
| 2020-03-02 |    pfizer   |      1      |
| 2020-03-02 | astrazeneca |      0      |
| 2020-03-02 |  coronavac  |      3      |

Após isso, a tabela deve ser remodelada para os valores de _vacina\_nome_ serem colunas e _paciente_id_ serem valores indexados pela data. A nova tabela deve ser:

|            | pfizer | astrazeneca | coronavac |
|:----------:|:------:|:-----------:|:---------:|
| 2020-03-02 |    1   |      1      |     2     |
| 2020-03-04 |   NaN  |     NaN     |     4     |
| 2020-03-07 |   NaN  |      1      |     1     |

Por último, deve reindexar a tabela para uma série de datas contínuas desde a ocorrẽncia da primeira 2ª dose até hoje e preencher as células faltantes com 0.


# Módulo de Visualização dos Dados

O módulo de visualização é implementado pelo _script_ `data_visualization.py` que recebe como argumentos o nome do arquivo que identifica o item a ser visualizado, a unidade federativa e o município a que os dados se referem.

Exemplo:
```console
$ python data_visualization.py demanda-vacinal AL MACEIO
```
A seguir, detalhamos a especificação da geração dos dados de visualização do item "Atraso de vacinação".

### Atraso de vacinação

* Objetivo:
    * Visualizar o número de pessoas que tomaram a segunda dose depois do prazo em cada dia.
* Entrada:
    * Tabela processada encontrada em:
        * datasets/AL/MACEIO/serie-atraso.csv
* SAÍDA:
    * Objeto representando a figura, de acordo com a especificação do objetivo.

#### Implementação do algoritmo

Basta carregar o dataframe da região escolhida, o eixo x será as datas, o eixo y será as quantidades e a cor será o tipo de vacina.
