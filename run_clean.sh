#!/bin/bash
. venv/bin/activate
cd src/carrega_dados/
python carrega_vacinacao_norm_banco.py
python carrega_vacinacao_limpa.py


