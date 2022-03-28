# Este é o arquivo que intermediará o acesso da pessoa às diferentes páginas do site.
from flask import render_template, request, redirect, url_for, flash, abort
from jinja2 import pass_context
from Flask_Reddit.forms import FormCriarConta, FormLogin, FormEditarPerfil, FormCriarPost
from Flask_Reddit import app, database
from Flask_Reddit.models import Post, Usuario
from Flask_Reddit import bcrypt, login_manager
# O objeto current_user será usado nos arquivos em html para puxar os dados do usuário, quando necessário.
from flask_login import login_user, logout_user, current_user, login_required
import os
import secrets
from PIL import Image

# Página home do site; mostrará os posts conforme forem publicados.
@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    # Note que o valor de retorno da função admite HTML.
    return render_template('home.html', posts=posts)


@app.route('/felipe')
def nova_area():
    return '<p>You\'ve just found a secret tag!</p>'

# Criei essa seção do site para deixar avisos importantes para mim.
@app.route('/README')
def readme():
    return render_template('README.html')

# Página em que os usuários do Reddit serão listados; é necessário estar logado para acessá-la (@login_required).
@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios = lista_usuarios)

# Uma pequena página de suporte ao usuário.
@app.route('/contato')
def contato():
    return render_template('contato.html')

# Página de login e cadastro do usuário. Ela utilizará alguns dos formulários criados em 'forms.py'.
@app.route('/cadastro-login', methods = ['GET', 'POST'])
def cadastrologin():
    # Invocando os formulários necessários.
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    # 'validade_on_submit' rodará as funções que começam com 'validate' automaticamente.
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        # Verificação de existência dos dados dos usuáros para o login.
        usuario = Usuario.query.filter_by(email = form_login.email.data).first()
        if bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember = form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail', 'alert-success')
            # O par_next será utilizado para redirecionar o usuário à página em que estava tentando acessar sem o devido login prévio
            # (páginas com o decorator @login_required).
            # Após essa irregularidade ser corrigida, ele poderá entrar nela.
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else: 
                return redirect(url_for('home'))
        else:
             flash(f'Dados Incorretos. Tente novamente!', 'alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        # Quando uma pessoa cria uma nova conta, sua senha cadastrada será criptografada.
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        # Registrando o novo usuário no banco de dados.
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('cadastrologin'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

# Daqui para baixo, criarei as páginas que só aparecerão para um usuário logado no site.

# Página de logout.
@app.route('/sair')
@login_required
def sair():
    # Esse método automaticamente fará o logout do usuário.
    logout_user()
    flash('Logout concluído', 'alert-success')
    # Após o procedimento, redirecionaremos o usuário para a página 'home'.
    return redirect(url_for('home'))

# Página que mostra as informações gerais do cadastrado.
@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static',filename = f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil = foto_perfil)

# Criação de um post.
@app.route('/post/criar', methods=['GET','POST'])
@login_required
def criar_post():
    # Invocando o formulário de posts.
    form = FormCriarPost()
    # Quando a pessoa clicar no botão de enviar o post, este será registrado no banco de dados.
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user) 
        database.session.add(post)
        database.session.commit()
        flash('Post publicado com sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)

def salvar_imagem(imagem):
    # Redefinindo o nome da imagem do usuário no banco de dados a fim de individualizá-la.
    codigo=secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo=nome + codigo + extensao
    # O novo nome da foto será <path><nome_original><codigo_token>.<extensao>
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil' ,nome_arquivo)
    # Compactando a imagem.
    tamanho = (400,400)
    # Reduzindo as proporções da imagem.
    imagem_reduzida=Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    # Salvando-a com o novo nome.
    imagem_reduzida.save(caminho_completo)

    return nome_arquivo

# Esta função listará todas as comunidades nas quais o usuário está inscrito.
def atualizar_comunidades(form):
    lista_comunidades = []
    for campo in form:
        # campo.name se refere ao nome da variável que armazena o campo.
        if 'com_' in campo.name and campo.data:
            # campo.label.text é o rótulo do campo apresentado ao usuário quando esse acessa o site.
            lista_comunidades.append(campo.label.text)

    return ';'.join(lista_comunidades)


# Editar o perfil.
@app.route('/perfil/editar', methods = ['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        # Alterando os dados de email e username.
        current_user.email = form.email.data
        current_user.username = form.username.data
        # Mudando a foto de perfil do usuário com a função 'salvar_imagem'.
        if form.foto_perfil.data:
            nome_imagem=salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil=nome_imagem
        # Armazenando todas as comunidades em que a pessoa se inscreveu.
        current_user.grupos = atualizar_comunidades(form)

        # Commitando as alterações
        database.session.commit()
        flash('Alterações efetuadas com sucesso','alert-success')
        return redirect(url_for('perfil'))
    # Este elif fará com que, quando a página de edição for carregada, os campos de email e username estejam automaticamente
    # preenchidos pelo email e username atuais do usuário.
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil=url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', form=form, foto_perfil=foto_perfil)

# Página de exibição de um determinado post quando clicado na página 'home'.
@app.route('/post/<post_id>', methods=['GET','POST'])
@login_required
def exibir_post(post_id):
    # Para exibir o post, tempos que buscar todas as suas informações na base de dados.
    post = Post.query.get(post_id)
    # Caso o usuário em questão seja dono do post, ele estará apto para modificá-lo.
    if current_user == post.autor:
        # O formulário 'FormCriarPost' com sua estrutura será reutilizado para a funcionalidade de modificação.
        form=FormCriarPost()
        # Assim como na função 'editar_perfil', este trecho de código permitirá que o formulário já esteja preenchido
        # com o título e corpo do post atuais.
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        # Quando o usuário editar o seu post, suas alterações serão incorporadas e confirmadas na base de dados do site, redirecionando-o
        # à página inicial.
        else:
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Edição concluída com sucesso!', 'alert-success')
            return redirect(url_for('home'))
    else:
        # Caso a pessoa não seja dona do post, o formulário de edição, obviamente, não aparecerá.
        form=None
    return render_template('post.html', post=post, form=form)

# Quando alguém quiser deletar o seu post, essa pessoa será redirecionada de maneira efêmera no qual a ação se cumprirá.
# Após isso, ela será redirecionada à página 'home'.
@app.route('/post/<post_id>/excluir', methods=['GET','POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    # Conferindo se a pessoa a deletar o post é, de fato, dona dele.
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído', 'alert-danger')
        return redirect(url_for('home'))
    else:
        # A função abort levará o usuário que não está apto a deletar a publicação a uma página de erro especial.
        abort(403)