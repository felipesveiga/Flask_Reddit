# Este arquivo será destinado à criação dos formulários.
# Cada formulário terá os seus campos com as suas restrições específicas (essas definidas no argumento 'validators').
from ast import Sub
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Email, EqualTo, DataRequired, Length, ValidationError
from Flask_Reddit.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField('Usuário', validators = [DataRequired(message = 'Informe um username.')])
    email = StringField('Email', validators= [DataRequired(message = 'Informe um E-mail'), Email(message = 'Endereço de E-mail inválido.')])
    senha = PasswordField('Senha', validators=[Length(min = 8, message = 'A senha deve ter ao menos 8 caracteres.')])
    confirmacao_senha = PasswordField('Confirme sua senha', validators=[DataRequired(message = 'Escreva uma senha.'),EqualTo('senha', message = 'O campo não está igual ao da senha informada.')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    # Função de validação que verificará se já existe uma conta cadastrada com o e-mail informado pela pessoa.
    # Nota: todas as funções de formulário cujo nome comece com 'validate' serão rodadas.
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email = email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado! Faça o seu login!')
        

class FormLogin(FlaskForm):
    email = StringField('Email', validators= [DataRequired(message = 'Insira um E-mail'), Email(message = 'Insira um E-mail válido')])
    senha = PasswordField('Senha', validators=[Length(min = 8, message = 'Lembrete: a senha deve ter ao menos 8 caracteres.', )])
    lembrar_dados = BooleanField('Lembrar senha')
    botao_submit_login = SubmitField('Login')

class FormEditarPerfil(FlaskForm):
    email=StringField('Email', validators =[DataRequired(message = 'Insira um novo E-mail'), Email(message='Insira um E-mail válido')] )
    username=StringField('Usuário', validators=[DataRequired('Insira um novo username')])
    # Campo para inserção de uma nova foto de perfil.
    foto_perfil = FileField(label='Alterar sua foto de perfil', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    # Os Booleans Fields abaixo permitirão ao usuário se inscrever nas comunidades de nosso Reddit.
    com_politics = BooleanField('Politics')
    com_sports = BooleanField('Sports')
    com_cucine = BooleanField('Cucine')
    com_memes = BooleanField('Memes')
    botao_submit_editarperfil=SubmitField('Confirmar Alterações')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email = email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado! Recorra a outro endereço')

class FormCriarPost(FlaskForm):
    titulo=StringField('Título do post', validators=[DataRequired(message='Campo não preenchido'), Length(1,30)])
    # Como explicado no arquivo 'models.py', o corpo dos posts será do tipo Text por admitir mensagens longas.
    corpo=TextAreaField('Texto do post', validators=[DataRequired(message='Campo não preenchido')])
    botao_submit=SubmitField('Enviar Post')