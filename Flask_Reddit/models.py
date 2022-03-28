# Aqui, estamos criando as tabelas do banco de dados do site.
# Teremos uma tabela com as informações dos usuários e outra sobre os posts publicados.
from Flask_Reddit import database, login_manager
from flask_login import UserMixin
from datetime import datetime

# Esta função será responsável por logar o usuário no site.
@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(id_usuario)

class Usuario(database.Model, UserMixin):
    # id será a primary key da tabela; será como se fosse um index padrão do pandas.
    id = database.Column(database.Integer, primary_key = True)
    # Aqui, estamos permitindo dois usuários terem o mesmo username, já que a coluna id será respinsável por individualizar cada
    # um deles.
    username = database.Column(database.String, nullable = False)
    email = database.Column(database.String, nullable = False, unique = True)
    senha = database.Column(database.String, nullable = False)
    # As fotos serão strings pois o que será armazenado é o nome do arquivo da foto de perfil.
    # O default indica a foto padrão de usuário (aquela que tem a silhueta de uma pessoa).
    foto_perfil = database.Column(database.String, default =  'default.png')
    posts = database.relationship('Post', backref = 'autor', lazy = True )
    # 'grupos' é equivalente à 'cursos' da versão do Lira.
    grupos = database.Column(database.String, nullable = False, default = 'Não Informado.')

class Post(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    titulo = database.Column(database.String, nullable = False)
    # Estamos definindo como Text pois o corpo do texto permitirá longas mensagens.
    corpo = database.Column(database.Text, nullable = False)
    # Caso houvesse parênteses em utcnow, o programa rodaria essa função neste exato instante e designaria o seu resultado
    # a todas as instâncias da clase Post.
    data_criacao = database.Column(database.DateTime, default = datetime.utcnow ,nullable = False)
    # Informando ao Python que a coluna 'id_usuario' é uma Foreign Key que ligará a tabela de posts à de usuários por meio do id
    # do autor.
    # Nota: o nome da classe passada em ForeignKey deve estar em minúsculas!
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable = False)
    