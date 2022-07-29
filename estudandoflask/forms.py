from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from estudandoflask.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):

    username= StringField("Nome de usuário", validators=[DataRequired()])
    email = StringField("E-mail",validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6,20)])
    confirmacao = PasswordField("Confirmação de Senha",validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField("Criar Conta")

    # Definindo função de validação
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Email já cadastrado!')

class FormLogin(FlaskForm):

    email = StringField("E-mail",validators=[DataRequired(message="Digite um endereço de email válido."), Email()])
    senha = PasswordField("Senha",validators=[DataRequired(message="Digite uma senha válida."), Length(6,20)])
    lembrar_dados = BooleanField("Lembrar Dados de Acesso")
    botao_submit_login = SubmitField("Fazer Login")


class FormEditarPerfil(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar foto de Perfil', validators=[FileAllowed(['jpg','png'])])
    botao_submit_editarperfil = SubmitField("Editar Perfil")

    # Validando se o email de edição já pertence a um outro usuário
    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first() # Recuperando usuário através do Email
            if usuario:
                raise ValidationError("Email já em uso!")