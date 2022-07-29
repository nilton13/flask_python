from flask import render_template, redirect, url_for, flash, request
from estudandoflask import app,database, bcrypt
from estudandoflask.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from estudandoflask.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route('/') # Criando Link de uma nova Página
def home(): # Função para mostrar algo na Página
    return render_template('home.html')

@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)

@app.route('/login', methods=['GET','POST'])
def login():
    form_login = FormLogin()
    form_criarConta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form :
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data) #Fazer o login e lembrar os dados.
            flash(f'Login feito com sucesso para o email {form_login.email.data}','alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Email e/ou senha incorretos', 'alert-danger')
    if form_criarConta.validate_on_submit() and 'botao_submit_criarconta' in request.form :
        senha_cript = bcrypt.generate_password_hash(form_criarConta.senha.data) #Encriptando senha
        usuario = Usuario(username=form_criarConta.username.data,
                          email=form_criarConta.email.data,
                          senha=senha_cript)
        #Adicionando usuário
        database.session.add(usuario)
        database.session.commit()

        flash(f'Conta criada com sucesso para o email {form_criarConta.email.data}','alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarConta=form_criarConta)

@app.route('/sair')
def sair():
    logout_user()
    flash(f'Logout feito com sucesso!', 'alert-warning')
    return redirect(url_for('home'))

@app.route('/perfil')
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)

@app.route('/post/criar', methods=['GET','POST'])
@login_required #Só acessa se o usuário estiver logado.
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post) # Adicionando a sessão no Banco de Dados
        database.session.commit() 
        flash('Post criado com sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)

# Cria e adiciona um código único ao nome do arquivo e altera o tamanho da imagem.
def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename) # Separando o nome da ex tensão
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)

    tamanho = (200,200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

@app.route('/perfil/editar', methods=['GET','POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash(f'Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET': #No carregamento da edição os Inputs ficarem preenchidos.
        form.email.data = current_user.email # O input recebe o email e nome de usuário do Usuário Logado.
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)