# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__, static_url_path = '/static')
# Deixar isso aqui para no dar erro 404.
#app._static_folder = ''
# Criando um token para o portal de login.
app.config['SECRET_KEY'] = 'd33e8d3e03f91c1dfbe7d7d5e8f09973'

# Criando a base de dados do site.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'

# Instanciando a base de dados.
database = SQLAlchemy(app)

# Criando o mecanismo de criptografia de senhas da base de dados.
bcrypt = Bcrypt(app)

# Criando o gerenciador de login do site. Ele que administrará o acesso do usuário à sua conta e 
# poderá bloquear o seu acesso a determinadas páginas sem o login prévio.
login_manager = LoginManager(app)
# Caso a pessoa tente acessar uma página restrita a usuários logados sem estar logada, ela será direcionada à área de login.
# Além disso, uma mensagem de alerta aparecerá explicando a impossibilidade de acesso à página desejada.
login_manager.login_view = 'cadastrologin'
login_manager.login_message = 'Faça seu Login para acessar a página'
login_manager.login_message_category = 'alert-info'

# Importando o arquivo routes para que as páginas sejam carregadas.
from Flask_Reddit import routes