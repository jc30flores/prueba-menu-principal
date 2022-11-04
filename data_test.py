import pandas as pd
import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

engine = create_engine('sqlite:///Hospital_db', connect_args={'check_same_thread': False}, echo=True)
app.Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def convertir_a_binario(foto):
    with open(foto, 'rb') as f:
        blob = f.read()
        
    return blob

@app.route("/")
@app.route("/creacion de datos")
def data_creation():
    return render_template('creacion_datos.html')

@app.route("/creacion de datos/hospitales", methods=['GET', 'POST'])
def creation_hospitals():
    if request.method == 'POST':
        if request.form['hospital'] and request.form['zona']:
            new_hospital = app.Hospitales(hospital=request.form['hospital'], zona=request.form['zona'])
            #session.add(new_hospital)
            #session.commit()
            df_hospital = pd.read_csv('hospitales.csv')
            df_hospital = df_hospital.append({'hospital': request.form['hospital'], 'zona': request.form['zona']}, ignore_index=True)
            df_hospital.to_csv('hospitales.csv', index=False)
            #flash(f'{new.hospital} Agregado con exito!')
            return render_template('hospitales_creation.html')
        else:
            return render_template('hospitales_creation.html')
    
    else:
        return render_template('hospitales_creation.html')

@app.route("/creacion de datos/isbm", methods=['GET', 'POST'])
def creation_isbm():
    if request.method == 'POST':
        new_idP = app.Id_Policlinico(policlinic_id=request.form['idP'], nombre=request.form['nombre'], cargo=request.form['cargo'], hospital=request.form['hospital'])
        #session.add(new_idP)
        #session.commit()
        #df_idP = pd.read_csv('policlinico.csv')
        #df_idP = df_idP.append({'policlinic_id': request.form['idP'], 'nombre': request.form['nombre'], 'cargo': request.form['cargo'], 'hospitales': request.form['name']}, ignore_index=True)
        #df_idP.to_csv('hospitales.csv', index=False)
        #flash(f'{new.nombre} Agregado con Exito!')
        return render_template('policlinico_creation.html')
    
    else:
        return render_template('policlinico_creation.html')

@app.route("/creacion de datos/supervisor_s", methods=['GET', 'POST'])
def creation_supervisor_s():
    if request.method == 'POST':
        if request.form['usuario'] and request.form['clave'] and request.form['correo'] and request.form['idP']:
            new_supervisor_s = app.Supervisor_S(usuario=request.form['usuario'], clave=request.form['clave'], correo=request.form['correo'], policlinic_id=request.form['idP'])
            #session.add(new_supervisor_s)
            #session.commit()
            #df_supervisor_s = pd.read_csv('supervisor_s.csv')
            #df_supervisor_s = df_supervisor_s.append({'usuario':request.form['usuario'], 'clave':request.form['clave'], 'correo':request.form['correo'], 'policlinic_id':request.form['idP']}, ignore_index=True)
            #df_supervisor_s.to_csv('supervisor_s.csv', index=False)
            #flash(f'{new.nombre} Agregado con Exito!')
            return render_template('supervisor_s_creation.html')
        else:
            return render_template('supervisor_s_creation.html')
    
    else:
        return render_template('supervisor_s_creation.html')

@app.route("/creacion de datos/supervisores", methods=['GET', 'POST'])
def creation_supervisores():
    if request.method == 'POST':
        if request.form['usuario'] and request.form['clave'] and request.form['correo'] and request.form['idP']:
            new_supervisores = app.Supervisor_S(usuario=request.form['usuario'], clave=request.form['clave'], correo=request.form['correo'], policlinic_id=request.form['idP'], superior_id=request.form['s_idP'])
            #session.add(new_supervisores)
            #session.commit()
            #df_supervisores = pd.read_csv('supervisores.csv')
            #df_supervisores = df_supervisores.append({'usuario':request.form['usuario'], 'clave':request.form['clave'], 'correo':request.form['correo'], 'policlinic_id':request.form['idP'], 'superior_id':request.form['s_idP']}, ignore_index=True)
            #df_supervisores.to_csv('supervisores.csv', index=False)
            #flash(f'{new.nombre} Agregado con Exito!')
            return render_template('supervisores_creation.html')
        else:
            return render_template('supervisores_creation.html')
    
    else:
        return render_template('supervisores_creation.html')
        

@app.route("/creacion de datos/coordinadores", methods=['GET', 'POST'])
def creation_coordinadores():
    if request.method == 'POST':
        if request.form['usuario'] and request.form['clave'] and request.form['correo'] and request.form['idP']:
            new_coordinadores = app.Coordinadores(usuario=request.form['usuario'], clave=request.form['clave'], correo=request.form['correo'], policlinic_id=request.form['idP'], superior_id=request.form['s_idP'])
            #session.add(new_coordinadores)
            #session.commit()
            #df_coordinadores = pd.read_csv('coordinadores.csv')
            #df_coordinadores = df_coordinadores.append({'usuario':request.form['usuario'], 'clave':request.form['clave'], 'correo':request.form['correo'], 'policlinic_id':request.form['idP'], 'superior_id':request.form['s_idP']}, ignore_index=True)
            #df_coordinadores.to_csv('coordinadores.csv', index=False)
            #flash(f'{new.nombre} Agregado con Exito!')
            return render_template('coordinadores_creation.html')
        else:
            return render_template('coordinadores_creation.html')
    
    else:
        return render_template('coordinadores_creation.html')

@app.route("/creacion de datos/medicos", methods=['GET', 'POST'])
def creation_medicos():
    if request.method == 'POST':
        
        if request.form['usuario'] and request.form['clave'] and request.form['correo'] and request.form['idP']:
            new_medicos = app.Medicos(usuario=request.form['usuario'], clave=request.form['clave'], correo=request.form['correo'], policlinic_id=request.form['idP'], superior_id=request.form['s_idP'], prov_o_trat=request.form['prov_o_trat'])  
            #session.add(new_medicos)
            #session.commit()
            df_medicos = pd.read_csv('medicos.csv')
            df_medicos = df_medicos.append({'usuario':request.form['usuario'], 'clave':request.form['clave'], 'correo':request.form['correo'], 'policlinic_id':request.form['idP'], 'superior_id':request.form['s_idP'], 'prov_o_trat':request.form['prov_o_trat']}, ignore_index=True)
            df_medicos.to_csv('medicos.csv', index=False)
            return render_template('medicos_creation.html')
        else:
            return render_template('medicos_creation.html')
    
    else:
        return render_template('medicos_creation.html')

@app.route("/creacion de datos/pacientes", methods=['GET', 'POST'])
def creation_pacientes():
    if request.method == 'POST':
        if request.form['n_afiliacion'] and request.form['nombre'] and request.form['clave'] and request.form['correo'] and request.form['edad'] and request.form['sexo'] and request.form['dui']:
            new_pacientes = app.Pacientes(n_afiliacion=request.form['n_afiliacion'], nombre=request.form['nombre'], usuario=request.form['dui'], clave=request.form['clave'], correo=request.form['correo'], edad=request.form['edad'], sexo=request.form['sexo'], dui=request.form['dui'], proveedor=True)
            #session.add(new_pacientes)
            #session.commit()
            #df_pacientes = pd.read_csv('pacientes.csv')
            #df_pacientes = df_pacientes.append({'n_afiliacion':request.form['n_afiliacion'], 'nombre':request.form['nombre'], 'usuario':request.form['usuario'], 'clave':request.form['clave'], 'correo':request.form['correo'], 'edad':request.form['edad'], 'sexo':request.form['sexo'], 'dui':request.form['dui']}, ignore_index=True)
            #df_pacientes.to_csv('pacientes.csv', index=False)
            return render_template('pacientes_creation.html')
        else:
            return render_template('pacientes_creation.html')
    
    else:
        return render_template('pacientes_creation.html')

if __name__ == '__main__':
    app.secret_key = "supersecretkey"
    app.debug = True
    app.run(host='0.0.0.0', port=8080)