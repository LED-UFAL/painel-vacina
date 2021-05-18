#!/bin/bash
. venv/bin/activate
cd src/carrega_dados/
python cria_tabela_staging_de_csv.py
