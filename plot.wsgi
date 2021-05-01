import sys 

activate_this = '/var/www/painel-vacina-venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '/var/www/painel-vacina')
from plot import server as application
