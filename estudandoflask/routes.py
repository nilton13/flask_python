from flask import render_template, redirect, url_for, flash, request
from estudandoflask import app,database, bcrypt
from estudandoflask.forms import FormLogin, FormCriarConta, FormEditarPerfil
from estudandoflask.models import Usuario
from flask_login import login_user, logout_user, current_user, login_required

lista_usuarios = ['Nilton', 'Naiane', 'Olivia']

@app.route('/') # Criando Link de uma nova Página
def home(): # Função para mostrar algo na Página
    return render_template('home.html')

@app.route('/usuarios')
@login_required
def usuarios():
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

@app.route('/post/criar')
@login_required #Só acessa se o usuário estiver logado
def criar_post():
    return render_template('criarpost.html')

@app.route('/perfil/editar', methods=['GET','POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        database.session.commit()
        flash(f'Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET': #No carregamento da edição os Inputs ficarem preenchidos.
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)