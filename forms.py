from flask_wtf import Form
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length, AnyOf
from flask_wtf.file import FileAllowed, FileField


class HospitalForm(Form):
    hospital = StringField('Hospital:', validators=[InputRequired()])
    zona = StringField('Zona:', validators=[InputRequired()])


class PersonalForm(Form):
    nombre = StringField('Nombre:', validators=[InputRequired()])
    profesion = StringField('Profesion:')
    n_junta = IntegerField('Numero de Junta:', validators=[InputRequired()])
    especialidad = StringField('Especialidad:')
    sub_especialidad = StringField('Sub-Especialidad:')
    cargo = SelectField('Cargo:', validators=[InputRequired()], choices=['Supervisor en Jefe SS', 'Supervisor en Jefe Occidental', 'Supervisor en Jefe Central', 'Supervisor en Jefe Oriental', 'Supervisor', 'Coordinador', 'Medico Proveedor', 'Establecimiento Proveedor', 'Medico Tratante'])
    fys = FileField('Firma y Sello:', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    correo = StringField('Email:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    hospital = SelectField('Hospital:', choices=[])


class PacienteForm(Form):
    n_afiliacion = IntegerField('Numero de Afiliacion', validators=[InputRequired()])
    nombre = StringField('Nombre:', validators=[InputRequired()])
    tipo_afiliacion = SelectField('Tipo de Afiliacion:', choices=['Hij@', 'Cotizante', 'Espos@'])
    estado = SelectField('Estado:',choices=['ACTIVO', 'INACTIVO'])
    edad = IntegerField('Edad:', validators=[InputRequired(), Length(min=1, max=2)])
    sexo = SelectField('Sexo:', validators=[InputRequired()], choices=['M', 'F'])
    correo = StringField('Email:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    dui = IntegerField('Numero de DUI:', validators=[InputRequired()])


class InicioSesion(Form):
    usuario = IntegerField('Numero de Junta:', validators=[InputRequired(), Length(min=4, max=5)])
    password = PasswordField('Contraseña:', validators=[InputRequired(), Length(min=8, max=32)])