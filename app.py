import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from importlib_metadata import method_cache
from numpy import NaN
from forms import HospitalForm, PacienteForm, PersonalForm, InicioSesion
from sqlalchemy import desc

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'secretkey123'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qceyghxggjkyrm:7c39ae324a34c9fd337d8ee1243a79b7ae12ca8392a661282cc5bb926b9088d3@ec2-44-199-22-207.compute-1.amazonaws.com:5432/d10pjdf7sfslvo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_table.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Column = db.Column
ForeignKey = db.ForeignKey
Integer = db.Integer
String = db.String
Date = db.Date 
Boolean = db.Boolean
Text = db.Text
Time = db.Time
BLOB = db.LargeBinary
relationship = db.relationship
Base = db.Model
Float = db.Float
#--------------------- CREACION DE LA TABLA DONDE SE ALMACENARAN TODOS LOS HOSPITALES Y SUS ZONAS ---------------------

class Hospitales(Base):
    __tablename__ = 'hospitales'
    """
    DATOS:

            id: numero unico que se le otorgara a cada hospital

            zona: Zona donde se encuentra el Hospital
            
            hospital: hospital al que este pertenece, esto solo aplica para: coordinadores y medicos.

            monto: Monto del hospital

    """
    
    id = Column(Integer, primary_key = True, autoincrement=True,  nullable=False)
    hospital = Column(String(), nullable=True)
    zona = Column(String(), nullable=False)
    monto = Column(Float, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'hospital': self.hospital,
            'zona': self.zona,
            'monto': self.monto
        }

#--------------------- CREACION DE LA TABLA DONDE SE ALMACENARAN TODOS LOS DATOS DE EL PERSONAL ---------------------

class Personal_isbm(Base):
    __tablename__ = 'personal'
    """
    DATOS:

            id: numero unico que se le otorgara en el sistema

            n_junta: Numero de junta (numero unico), este sera tambien su usuario
            
            nombre: Nombre de la persona
            
            sexo: genero de la persona = [M | F] Masculino o Femenino
            
            edad: edad de la persona
            
            nacimiento: fecha de nacimiento de la persona
            
            profesion: Profesion de la persona
            
            especialidad: Especialidad de la persona
            
            sub_especialidad: sub especialidades de las especialidades (Solo si es necesario)
            
            cargo: Cargo que ejecuta
                        
            hospital: hospital al que pertenece (si pertenece a uno)
            
            correo: correo de la persona
            
            password: password creada por la persona
            
            monto: Monto que se ha generado. ***AREGLAR ESTO DESPUES***
            
            id_jerarquico: numero unico que indica el nivel jerarquico en el que se encuentra, 
                           el primer numero indica el nivel, 
                           el segundo el cargo si hay varios cargos en un nivel (solo si es necesario)
                           el tercero es el numero unico de id (cuando hay varias personas con el mismo cargo)
                           
                           ej: Supervisor Superior en Jefe = "1"
                               Supervisor en Jefe por zona = "2.id" ---> id es el numero unico de la persona.
                               Supervisores = "3.id"
                               Coordinadores, Medicos Proveedores, Establecimientos Proveedores = "4.cargo.id" 
                                                                                                               ---> cargo indica el numero segun el cargo (1: Coordinador, 2: Medico Proveedor, 3: Establecimiento Proveedor)
                                                                                                               ---> id indica el numero unico de la persona. 
                               Medicos Tratantes: "5.id"
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_jerarquico = Column(String(11), nullable=True)
    n_junta = Column(Integer, nullable=False)
    nombre = Column(String(), nullable=False)
    sexo = Column(String(), nullable=True)
    edad = Column(Integer, nullable=True)
    nacimiento = Column(Date, nullable=True)
    profesion  = Column(Text, nullable=True)
    especialidad = Column(Text, nullable=True)
    sub_especialidad = Column(Text, nullable=True)
    cargo = Column(String(), nullable=False)
    hospital = Column(Text, nullable=True)
    correo = Column(Text, nullable=True)
    password = Column(String(20), nullable=False)
    monto = Column(Float, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'id_jerarquico': self.id_jerarquico,
            'n_junta': self.n_junta,
            'nombre': self.nombre,
            'sexo': self.sexo,
            'edad': self.edad,
            'nacimiento': self.nacimiento,
            'profesion': self.profesion,
            'especialidad': self.especialidad,
            'sub_especialidad': self.sub_especialidad,
            'cargo': self.cargo,
            'hospital': self.hospital,
            'correo': self.correo,
            'password': self.password,
            'monto': self.monto
        }

#--------------------- CREACION DE LA TABLA PARA ALMACENAR LAS FIRMAS Y SELLOS ---------------------

class FirmasySellos(Base):
    __tablename__ = 'firmasysellos'
    """
    DATOS:

            id: numero unico que se obtiene de el id de el personal

            fys: imagen BLOB de la firma y sello de la persona

    """
    
    id = Column(Integer, primary_key = True, autoincrement=True, nullable=False)
    personal_id = Column(Integer, ForeignKey('personal.id'), nullable=False)
    fys = Column(BLOB, nullable=False)
    personal = relationship(Personal_isbm)
    

    @property
    def serialize(self):
        return {
            'id': self.id,
            'personal_id': self.personal_id,
            'fys': self.fys,
        }
#--------------------- CREACION DE LA TABLA PARA ALMACENAR LOS DATOS DE LOS PACIENTES ---------------------

class Pacientes(Base):
    __tablename__ = 'pacientes'
    """
    DATOS:

            n_afiliacion: numero de afiliacion unico que tiene cada paciente

            tipo_afiliacion: Tipo de afiliacion, si es ---> [Cotizante, Hij@, Esposo, Esposa]

            estado: Estado en el que se encuentra el afiliado ---> [Activo o Inactivo]
            
            nombre: nombre del paciente

            password: clave creada por el usuario para ingresar a su perfil (default numero de afiliacion + primer nombre en minusculas (sin espacios))
            
            correo: correo electronico del paciente

            edad: edad del paciente
            
            sexo: sexo / genero del paciente, puede ser ---> [Masulino, Femenino]

            dui: Numero de DUI del paciente, sin guiones
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    n_afiliacion = Column(Integer, nullable=False)
    tipo_afiliacion = Column(String(10), nullable=True)
    estado = Column(String(8), nullable=True)
    nombre = Column(String(), nullable=False)
    password = Column(Text, nullable=False)
    correo = Column(String(), nullable=True)
    edad = Column(Integer, nullable=True)
    sexo = Column(String(), nullable=True)
    nacimiento = Column(Date, nullable=True)
    dui = Column(Integer, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'n_afiliacion': self.n_afiliacion,
            'tipo_afiliacion': self.tipo_afiliacion,
            'estado': self.estado,
            'nombre': self.nombre,
            'password': self.password,
            'correo': self.correo,
            'edad': self.edad,
            'sexo': self.sexo,
            'nacimiento': self.nacimiento,
            'dui': self.dui
        }

#--------------------- CREACION DE LAS TABLAS DE LOS DIFERENTES FORMULARIOS ---------------------

class Formulario_C(Base):
    __tablename__ = 'formularioC'
    """
    DATOS:

            formulario_id: consta de una letra o varias que indican el tipo de formulario en este caso "C" para el formulario C, 
                           y le sigue un guion "-" y el numero de id
            
            amb_hosp: determina si el paciente es ambulatorio o hospitalizado
            
            lugar: ****PREGUNTAR A CARLOS SOBRE ESTE CAMPO****
            
            fecha: ****PREGUNTAR A CARLOS SOBRE ESTE CAMPO****
            
            afiliacion: numero unico del paciente, del cual se extrae de la class Pacientes
            
            nombre: nombre del paciente

            edad: edad del paciente

            sexo: sexo del paciente [Masculino o Femenino]
            
            diagnostico: diagnostico del medico
            
            exam_sol: Examen Solicitado
            
            esp_medico_sol: Especialidad del Medico Solicitante
            
            resumen_clinico: resumen clinico del paciente
            
            estudio: Estudio previo que sustentan la solicitud del presente examen
            
            inf_obt: Informacion que se espera obtener con el examen solicitado
            
            ofre_pte: Lo que el medico espera ofrecer al paciente con el resultado del examen

            solicitante_fys: firma y sello del medico solicitante

            autoriza_fys = firma y sello del medico que autoriza
            
            fecha_aut: fecha en la que fue autorizado el formulario
            
            lab_realizar: Laboratorio donde se realazara el examen solicitado
            
            observaciones: Observaciones del medico que autoriza el formulario

            tac: TAC   

            rmn: RMN
            
            angiotac: ANGIOTAC
            
            electromiografia: ELECTROMIOGRAFIA
            
            centellograma: CENTELLOGRAMA
            
            holter: HOLTER
            
            neuroconduccion: NEUROCONDUCCION  
            
            mapa: MAPA
            
            angio_selectiva: ANGIOGRAIA SELECTIVA
            
            pacientes: relationship() que se mantiene con la class Pacientes
    """
    
    id = Column(Integer, autoincrement=True, nullable=False)
    formulario_id = Column(String(), primary_key=True, nullable=False)
    amb_hosp = Column(String(13), nullable=False)
    lugar = Column(String(), nullable=False)
    fecha = Column(Date, nullable=False)

    afiliacion = Column(Integer, ForeignKey('pacientes.id'))
    nombre = Column(String(), nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(String(), nullable=False)

    diagnostico = Column(String(), nullable=False)
    exam_sol = Column(String(), nullable=False)
    esp_medico_sol = Column(String(), nullable=False)
    resumen_clinico = Column(Text, nullable=False)
    estudio = Column(String(), nullable=False)
    inf_obt = Column(Text, nullable=False)
    ofre_pte = Column(Text, nullable=False)
    solicitante_fys = Column(BLOB, nullable=True)
    
    #---datos que debe rellenar ISBM
    autoriza_fys = Column(BLOB, nullable=True)
    fecha_aut = Column(Date, nullable=True)
    lab_realizar = Column(String(), nullable=True)
    observaciones = Column(Text, nullable=True)

    tac = Column(Boolean, nullable=True)    
    rmn = Column(Boolean, nullable=True)
    angiotac = Column(Boolean, nullable=True)
    electromiografia = Column(Boolean, nullable=True)
    centellograma = Column(Boolean, nullable=True)
    holter = Column(Text, nullable=True)
    neuroconduccion = Column(Boolean, nullable=True)    
    mapa = Column(Boolean, nullable=True)
    angio_selectiva= Column(Boolean, nullable=True)

    pacientes = relationship('Pacientes')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'formulario_id': self.formulario_id,
            'amb_hosp': self.amb_hosp,
            'lugar': self.lugar,
            'fecha': self.fecha,
            'afiliacion': self.afiliacion,
            'nombre': self.nombre,
            'edad': self.edad,
            'sexo':self.sexo,
            'diagnostico': self.diagnostico,
            'exam_sol': self.exam_sol,
            'esp_medico_sol': self.esp_medico_sol,
            'resumen_clinico': self.resumen_clinico,
            'estudio': self.estudio,
            'inf_obt': self.inf_obt,
            'ofre_pte': self.ofre_pte,
            'solicitante_fys': self.solicitante_fys,
            'autoriza_fys': self.autoriza_fys,
            'fecha_aut': self.fecha_aut,
            'lab_realizar': self.lab_realizar,
            'observaciones': self.observaciones,
            'tac': self.tac,
            'rmn': self.rmn,
            'angiotac': self.angiotac,
            'electromiografia': self.electromiografia,
            'centellograma': self.centellograma,
            'holter': self.holter,
            'neuroconduccion': self.neuroconduccion,
            'mapa': self.mapa,
            'angio_selectiva': self.angio_selectiva
        }


class Formulario_B(Base):
    __tablename__ = 'formularioB'
    """
    DATOS:
            formulario_id: consta de una letra o varias que indican el tipo de formulario en este caso "B" para el formulario B, y le sigue un guion "-" y el numero de id
            
            elec_emer: determina si el paciente es electivo o de Emergencia
            
            lugar: ****PREGUNTAR A CARLOS SOBRE ESTE CAMPO****
            
            fecha: ****PREGUNTAR A CARLOS SOBRE ESTE CAMPO****
            
            afiliacion: numero unico del paciente, del cual se extrae de la class Pacientes
            
            nombre: nombre del paciente

            edad: edad del paciente

            sexo: sexo del paciente [Masculino o Femenino]
            
            diagnostico: diagnostico preoperatorio
            
            proced_quiru: Procedimiento Quirurgico a realizar
            
            esp_cirujano: Especialidad del Cirujano
            
            fecha_a_realizar: Fecha proyectaada a realizar la cirugia
            
            resumen: Resumen de la historia Clinica del paciente
            
            resultados_gab: Resultados de estudios de Gabinete que sustentan el diagnostico
            
            eval_pre: Evaluacion Preoperatorio
            
            ht: *PREGUNTAR A CARLOS*
            
            hb: *PREGUNTAR A CARLOS*
            
            tipeo_rh: *PREGUNTAR A CARLOS*
            
            glicemia: *PREGUNTAR A CARLOS*
            
            ego: *PREGUNTAR A CARLOS*
            
            otros: *PREGUNTAR A CARLOS*
            
            nombre_e: Nombre del paciente o encargado de aceptacion del procedimiento
            
            dui_e: DUI del paciente o encargado de aceptacion del procedimiento
            
            firma_e = Firma del paciente o encargado de aceptacion del procedimiento (formato Blob)

            medico_fys = id del medico para agregar firma y sello del medico tratante
                        
            fecha_aut: fecha en la que fue autorizado el formulario
            
            auto_proc_medico: Autorizacion Tecnica de Procedimiento Medico

            sello: sello de quien autoriza ----**CONSULTAR CON CARLOS**----
            
            observaciones: Observaciones del medico que autoriza el formulario
            
            pacientes: relationship() que se mantiene con la class Pacientes

            medico_tratante: relationship() que se mantiene con la class Medicos_Tratantes

    """
    
    id = Column(Integer, autoincrement=True, nullable=False)
    formulario_id = Column(String(), primary_key=True, nullable=False)
    elec_emer = Column(String(11), nullable=False)
    lugar = Column(String(), nullable=False)
    fecha = Column(Date, nullable=False)
    
    afiliacion = Column(Integer, ForeignKey('pacientes.id'))
    nombre = Column(String(), nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(String(), nullable=False)
    
    diagnostico = Column(String(), nullable=False)
    proced_quiru = Column(String(), nullable=False)
    esp_cirujano = Column(String(), nullable=False)
    fecha_a_realizar = Column(Date, nullable=False)
    resumen = Column(Text, nullable=False)
    resultados_gab = Column(Text, nullable=True)
    eval_pre = Column(Text, nullable=True)
    ht = Column(Boolean, nullable=True)    
    hb = Column(Boolean, nullable=True)
    tipeo_rh = Column(Boolean, nullable=True)
    glicemia = Column(Boolean, nullable=True)
    ego = Column(Boolean, nullable=True)
    otros = Column(Text, nullable=True)

    nombre_e = Column(String(), nullable=False)
    dui_e = Column(Integer, nullable=False)
    firma_e = Column(BLOB, nullable=False)

    medico_fys = Column(Integer, ForeignKey('personal.id'), nullable=False)
    auto_proc_medico = Column(String(), nullable=True)
    fecha_aut = Column(Date, nullable=True)
    sello = Column(BLOB, nullable=True)
    observaciones = Column(Text, nullable=True)
    pacientes = relationship(Pacientes)
    medico_tratante = relationship(Personal_isbm)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'formulario_id': self.formulario_id,
            'elec_emer': self.elec_emer,
            'lugar': self.lugar,
            'fecha': self.fecha,
            'afiliacion': self.afiliacion,
            'nombre': self.nombre,
            'edad': self.edad,
            'sexo': self.sexo,
            'diagnostico': self.diagnostico,
            'proced_quiru': self.proced_quiru,
            'esp_cirujano': self.esp_cirujano,
            'fecha_a_realizar': self.fecha_a_realizar,
            'resumen': self.resumen,
            'resultados_gab': self.resultados_gab,
            'eval_pre': self.eval_pre,
            'ht': self.ht,
            'hb': self.hb,
            'tipeo_rh': self.tipeo_rh,
            'glicemia': self.glicemia,
            'ego': self.ego,
            'otros': self.otros,
            'nombre_e': self.nombre_e,
            'dui_e': self.dui_e,
            'firma_e': self.firma_e,
            'medico_fys': self.medico_fys,
            'fecha_aut': self.fecha_aut,
            'sello': self.sello,
            'auto_proc_medico': self.auto_proc_medico,
            'observaciones': self.observaciones
        }


class Prorroga_Hospitalaria(Base):
    __tablename__ = 'prorroga_hospitalaria'
    """
    DATOS:
            formulario_id: consta de una letra o varias que indican el tipo de formulario en este caso "PH" 
                           para el formulario Prorroga Hospitalaria, y le sigue un guion "-" y el numero de id

            hospital: Nombre del hospital que solicita el formulario
                                    
            afiliacion: numero unico del paciente, del cual se extrae de la class Pacientes

            nombre: nombre del paciente

            edad: edad del paciente

            sexo: sexo del paciente [Masculino o Femenino]

            beneficiario: tipo de beneficiario [cotizante, conyuge, hij@s]

            fecha: fecha de ingreso

            hora: hora de ingreso
                        
            diagnostico: diagnostico de ingreso

            diagnostico_ins: diagnostico de instancia hospitalaria

            evl_paciente: evolucion del paciente
            
            proced_quiru: Procedimiento Quirurgico realizado

            justificacion: justificacion o criterios para la solicitud de la prorroga

            dias_sol: numero de dias solicitados

            solicitante_fys: firma y sello del solicitante

            coordinador_fys: firma y sello del coordinador del hospital

            apoyo_isbm_fys: firma y sello del medico de apoyo del ISBM
            
            ---Espacio del ISBM---

            dias_aut: numero de dias autorizados

            observaciones: Observaciones del medico que autoriza el formulario

            lugar: lugar donde fue autorizado
            
            fecha_aut: fecha en la que fue autorizado el formulario
                                    
            pacientes: relationship() que se mantiene con la class Pacientes

            coordinadores: relationship() que se mantiene con la class Coordinadores

            hospitales: relationship() que se mantiene con la class hospitales

    """
    
    id = Column(Integer, autoincrement=True, nullable=False)
    formulario_id = Column(String(), primary_key=True, nullable=False)
    hospital = Column(Integer, ForeignKey('hospitales.id'), nullable=False)

    #DATOS DEL PACIENTE
    afiliacion = Column(Integer, ForeignKey('pacientes.id'))
    nombre = Column(String(), nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(String(), nullable=False)
    beneficiario = Column(String(), nullable=False)

    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=True)
    diagnostico = Column(Text, nullable=False)
    diagnostico_ins = Column(Text, nullable=True)
    evl_paciente = Column(Text, nullable=True)
    proced_quiru = Column(Text, nullable=True)
    justificacion = Column(Text, nullable=True)
    dias_sol = Column(Integer, nullable=False)

    #SELLOS Y FIRMAS
    solicitante_fys = Column(BLOB, nullable=True)
    coordinador_fys = Column(Integer, ForeignKey('personal.id'), nullable=True)
    apoyo_isbm_fys = Column(BLOB, nullable=True)
    
    #---datos que debe rellenar ISBM
    dias_aut = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)
    lugar = Column(String(), nullable=True)
    fecha_aut = Column(Date, nullable=True)
    pacientes = relationship(Pacientes)
    coordinadores = relationship(Personal_isbm)
    hospitales = relationship(Hospitales)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'formulario_id': self.formulario_id,
            'hospital': self.hospital,
            'afiliacion': self.afiliacion,
            'nombre': self.nombre,
            'edad': self.edad,
            'sexo': self.sexo,
            'beneficiario': self.beneficiario,
            'fecha': self.fecha,
            'hora': self.hora,
            'diagnostico': self.diagnostico,
            'diagnostico_ins': self.diagnostico_ins,
            'evl_paciente': self.evl_paciente,
            'proced_quiru': self.proced_quiru,
            'justificacion': self.justificacion,
            'dias_sol': self.dias_sol,
            'solicitante_fys': self.solicitante_fys,
            'coordinador_fys': self.coordinador_fys,
            'apoyo_isbm_fys': self.apoyo_isbm_fys,
            'dias_aut': self.dias_aut,
            'observaciones': self.observaciones,
            'lugar': self.lugar,
            'fecha_aut': self.fecha_aut,
            'observaciones': self.observaciones
        }


class Boleta_Entrega_Medicamentos(Base):
    __tablename__ = 'boleta_entrega_medicamentos'
    """
    DATOS:

            formulario_id: numero unico del formulario con el formato 'BEM-id' 
                           BEM indica el tipo de formulario: Boleta de Entrega de Medicamentos y se le agrega el id
            
            policlinic_id: id del policlinico del medico/enfermera que esta creando la boleta
            
            afiliacion: numero de afiliacion del paciente
            
            nombre: nombre del paciente
            
            edad: edad del paciente
            
            dui: DUI del paciente
            
            firma: firma del paciente formato Blob
            
            descripcion: descripcion del medicamente que se le entregara al paciente
            
            cantidad: cantidad del medicamente que se le brindara al paciente
            
            enfermera_fys: firma y sello de la enferma encargada
            
            pacientes: relationship() que se mantiene con la class Pacientes
            
            id_policlinico: relationship() que se mantiene con la class Id_Policlinico
    """

    id = Column(Integer, autoincrement=True, nullable=False)
    formulario_id = Column(String(), primary_key=True, nullable=False)
    policlinic_id = Column(Integer, ForeignKey('personal.id'), nullable=False)
    afiliacion = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    nombre = Column(String(), nullable=False)
    edad = Column(Integer, nullable=False)
    dui = Column(Integer, nullable=True)
    firma = Column(BLOB, nullable=True)
    descripcion = Column(Text, nullable=True)
    cantidad = Column(String(), nullable=True)
    enfermera_fys = Column(BLOB, nullable=True)
    pacientes = relationship(Pacientes)
    id_policlinico = relationship(Personal_isbm)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'formulario_id': self.formulario_id,
            'policlinic_id': self.policlinic_id,
            'afiliacion': self.afiliacion,
            'nombre': self.nombre,
            'edad': self.edad,
            'dui': self.dui,
            'firma': self.firma,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'enfermera_fys': self.enfermera_fys,
        }


class Consentimiento_Informado(Base):
    __tablename__ = 'consentimiento_informado'
    """
    DATOS:

            formulario_id: numero unico del formulario en formato 'CI-id'
                           'CI' indica el tipo de formulario: Consentimiento Informado, y se le agrega el id
            
            policlinic_id: id del policlinico del medico/enfermera que esta creando la boleta
            
            afiliacion: numero de afiliacion del paciente
            
            nombre: nombre del paciente
            
            edad: edad del paciente
            
            sexo: sexo del paciente

            pr_quirurgico: Nombre del procedimiento quirurgico de diagnostico o de tratamiento que se va a realizar

            med_util: Nombres de medicamentos y dosis a utilizar

            anestesia: Tipo de anestesia que se utilizara

            consentimiento: True / False, si el paciente acepta el consentimiento o no

            declaracion_1: respuesta del paciente sobre la primera declaracion 

            declaracion_1_1: respuesta del paciente sobre la segunda declaracion 
            
            declaracion_1_2: respuesta del paciente sobre la tercera declaracion

            declaracion_4: respuesta del paciente sobre la cuarta declaracion

            firma_p: firma del paciente o del responsable de este

            dui_p: numero de DUI del paciente o del responsable de este

            firma_t: firma de un testigo

            dui_t: numero de DUI de un testigo
            
            medico: nombre del Medico Tratante encargado del Consentimiento Informado

            firma_sello: firma y sello del Medico Tratante

            lugar: lugar donde se esta haciendo el Consentimiento Informado

            fecha: fecha en la cual fue aceptado o rechazado el consentimiento informado
            
            pacientes: relationship() que se mantiene con la class Pacientes
            
            id_policlinico: relationship() que se mantiene con la class Id_Policlinico

            medico_tratante: relationship() que se mantiene con la class Medicos_Tratantes
    """

    id = Column(Integer, autoincrement=True, nullable=False)
    formulario_id = Column(String(), primary_key=True, nullable=False)
    policlinic_id = Column(Integer, ForeignKey('personal.id'), nullable=False)

    #Datos de Identificacion
    afiliacion = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    nombre = Column(String(), nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(String(), nullable=False)

    #Informacion Tecnica
    pr_quirurgico = Column(String(), nullable=False)
    med_util = Column(String(), nullable=True)
    anestesia = Column(String(), nullable=True)

    #Declaracion del paciente o responsable de este
    consentimiento = Column(Boolean, nullable=False)
    declaracion_1 = Column(Text, nullable=True)
    declaracion_1_1 = Column(Text, nullable=True)
    declaracion_1_2 = Column(Text, nullable=True)
    declaracion_4 = Column(Text, nullable=True)
    firma_p = Column(BLOB, nullable=False)
    dui_p = Column(Integer, nullable=False)
    firma_t = Column(BLOB, nullable=True)
    dui_t = Column(Integer, nullable=True)

    #Declaraciones y Firmas
    medico = Column(String(), nullable=True)
    firma_sello = Column(Integer, ForeignKey('personal.id'), nullable=True)

    #Lugar y Fecha
    lugar = Column(String(), nullable=True)
    fecha = Column(Date, nullable=False)
   
    pacientes = relationship(Pacientes)
    id_policlinico = relationship(Personal_isbm, foreign_keys=[policlinic_id])
    medico_tratante = relationship(Personal_isbm, foreign_keys=[firma_sello])

    @property
    def serialize(self):
        return {
            'id': self.id,
            'formulario_id': self.formulario_id,
            'policlinic_id': self.policlinic_id,
            'afiliacion': self.afiliacion,
            'nombre': self.nombre,
            'edad': self.edad,
            'sexo': self.sexo,
            'pr_quirurgico': self.pr_quirurgico,
            'med_util': self.med_util,
            'anestesia': self.anestesia,
            'consentimiento': self.consentimiento,
            'declaracion_1': self.declaracion_1,
            'declaracion_1_1': self.declaracion_1_1,
            'declaracion_1_2': self.declaracion_1_2,
            'declaracion_4': self.declaracion_4,
            'firma_p': self.firma_p,
            'dui_p': self.dui_p,
            'firma_t': self.firma_t,
            'dui_t': self.dui_t,
            'medico': self.medico,
            'firma_sello': self.firma_sello,
            'lugar': self.lugar,
            'fecha': self.fecha
        }



#--------------------- CREACION DE LAS TABLAS DE LOS PROCESOS DE LOS FORMULARIOS ---------------------

class Formularios(Base):
    __tablename__ = 'formularios'
    """
    DATOS:
            formulario_id: indica el id del formulario que se esta procesando/creando, 
                           para buscar los datos del formulario en la class del formulario al que pertenece
            
            creado_por: contiene el id del policlinico de la persona quien esta creando el formulario, 
                        asi podremos buscar sus datos en Id_policlinico, saber su cargo, 
                        y luego buscar sus datos en la class segun el cargo que tenga.
            
            estado: se refiere al estado en el que se encuentra el formulario [ACEPTADO, RECHAZADO, EN ESPERA], 
                    predeterminadamente se agrega como EN ESPERA.
            
            terminado: True si el proceso ha terminado, ya sea porque fue RECHAZADO, 
                       o porque ya se termino todo el proceso con el paciente, 
                       y False si este sigue ACEPTADO pero no se ha terminado el proceso con el paciente, o si esta EN ESPERA.

            id_policlinico: relationship() que se mantiene con la class Id_Policlinico

    """
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    formulario_id = Column(String(), nullable=False)
    creado_por = Column(Integer, ForeignKey('personal.id'), nullable=False)
    estado = Column(String(10), nullable=False)
    terminado = Column(Boolean, nullable=False)
    id_policlinico = relationship(Personal_isbm)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'formulario_id': self.formulario_id,
            'creado_por': self.creado_por,
            'estado': self.estado,
            'terminado': self.terminado
        }

#--------------------- CREACION DE LAS TABLAS DONDE SE ALMACENARAN LOS MENSAJES DE TODOS LOS TRABJADORES ---------------------

class Mensajes(Base):
    __tablename__ = 'mensajes'
    """
    DATOS:
            mensaje: mensaje sin limite de caracteres para comunicarse entre los trabajadores para informar algo de urgencia
            
            remitente: contiene el id del policlinico o el numero de afiliacion de la persona quien esta creando y enviando el mensaje, 
                        asi podremos buscar sus datos en Id_policlinico o en Pacientes, saber su cargo, 
                        y luego buscar sus datos en la class segun el cargo que tenga.
            
            estado: se refiere al estado en el que se encuentra el mensaje [Enviado, Enviado, Recibido, Leido], 
                    predeterminadamente se agrega como Enviando.
            
            destino: contiene el id del policlinico o numero de afiliacion de la persona que recibe o recibira el mensaje.  

            urgente: el mensaje debe ser revisado de inmediato, lleva un alto grado de importancia          

            id_policlinico: relationship() que se mantiene con la class Id_Policlinico

    """
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    mensaje = Column(Text, nullable=False)
    remitente = Column(Integer, nullable=False)
    estado = Column(String(), nullable=False)
    destino = Column(Integer, ForeignKey('personal.id'), nullable=False)
    urgente = Column(Boolean, nullable=True) #Investigar como dejar el valor predeterminado.
    id_policlinico = relationship(Personal_isbm)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'mensaje': self.mensaje,
            'remitente': self.remitente,
            'estado': self.estado,
            'destino': self.destino,
            'urgente': self.urgente
        }


#--------------------- CREACION DE LAS TABLAS DONDE SE ALMACENARAN LAS AGENDAS(CITAS/CITAS DE FORMULARIOS) ---------------------


class Agenda_Citas(Base):
    __tablename__ = 'agenda_citas'
    """
    DATOS:
            mensaje: mensaje sin limite de caracteres para comunicarse entre los trabajadores para informar algo de urgencia
            
            policlinic_id: id del policlinico del medico con el que hace la cita

            zona: la zona donde puede presentarse el paciente           

            hospital: hospital donde se tendra que presentar para la cita

            paciente: nombre del paciente que esta haciendo la cita

            afiliacion: numero de afiliacion del paciente

            fecha: fecha en la que se programara la cita

            hora: hora a la cual sera citado el paciente

            estado: estado en el que se encuentra la cita, ACEPTADA, RECHAZADA, EN ESPERA, TERMINADA.

            id_policlinico: relationship() que se mantiene con la class Id_Policlinico

            hospitales: relationship() que se mantiene con la class Hospitales

            pacientes: relationship() que se mantiene con la class Pacientes

    """
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    policlinic_id = Column(Integer, ForeignKey('personal.id'))
    hospital = Column(Integer, ForeignKey('hospitales.id'))
    zona = Column(String())
    paciente = Column(String(), nullable=False)
    afiliacion = Column(Integer, ForeignKey('pacientes.id'))
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String(10), nullable=False)
    id_policlinico = relationship(Personal_isbm)
    hospitales = relationship(Hospitales)
    pacientes = relationship(Pacientes)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'policlinic_id': self.policlinic_id,
            'hospital': self.hospital,
            'zona': self.zona,
            'paciente': self.paciente,
            'afiliacion': self.afiliacion,
            'fecha': self.fecha,
            'hora': self.hora,
            'estado': self.estado
        }

class Agenda_Formularios(Base):
    __tablename__ = 'agenda_formularios'
    """
    DATOS:
            mensaje: mensaje sin limite de caracteres para comunicarse entre los trabajadores para informar algo de urgencia
            
            policlinic_id: id del policlinico del medico con el que hace la cita

            autorizado_por: id del policlinico de la persona que autorizo la cita del fomulario

            formulario_id: id del formulario del cual se esta solicitando la cita

            zona: la zona donde puede presentarse el paciente           

            hospital: hospital donde se tendra que presentar para la cita

            paciente: nombre del paciente que esta haciendo la cita

            afiliacion: numero de afiliacion del paciente

            fecha: fecha en la que se programara la cita

            hora: hora a la cual sera citado el paciente

            estado: estado en el que se encuentra la cita, PROGRAMADA, TERMINADA.

            id_policlinico: relationship() que se mantiene con la class Id_Policlinico

            hospitales: relationship() que se mantiene con la class Hospitales

            pacientes: relationship() que se mantiene con la class Pacientes

    """
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    policlinic_id = Column(Integer, ForeignKey('personal.id'))
    autorizado_por_id = Column(Integer, ForeignKey('personal.id'))
    formulario_id = Column(Integer, ForeignKey('formularios.id'))
    hospital = Column(Integer, ForeignKey('hospitales.id'))
    zona = Column(String(), nullable=True)
    paciente = Column(String(), nullable=False)
    afiliacion = Column(Integer, ForeignKey('pacientes.id'))
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String(10), nullable=False)

    policlinic = relationship(Personal_isbm, foreign_keys=[policlinic_id])
    autorizado_por = relationship(Personal_isbm, foreign_keys=[autorizado_por_id])

    hospitales = relationship(Hospitales)
    pacientes = relationship(Pacientes)
    formularios = relationship(Formularios)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'policlinic_id': self.policlinic_id,
            'autorizado_por_id': self.autorizado_por_id,
            'formulario_id': self.formulario_id,
            'hospital': self.hospital,
            'zona': self.zona,
            'paciente': self.paciente,
            'afiliacion': self.afiliacion,
            'fecha': self.fecha,
            'hora': self.hora,
            'estado': self.estado
        }

#with app.app_context():
#    db.create_all()
session = db.session

@app.route("/")
@app.route("/hospital-project")
def inicio():
    return render_template('starting.html')

@app.route("/hospital-project/creacion de datos", methods=['GET', 'POST'])
def data_creation():
    form = HospitalForm()
    if request.method == 'POST':
        new_hospital = Hospitales(hospital=request.form['hospital'], zona=request.form['zona'])
        session.add(new_hospital)
        session.commit()
        flash("Los Datos fueron agregados con exito!")
        return render_template('creacion_datos.html', form=form)
    
    else:
        return render_template('creacion_datos.html', form=form)

@app.route("/hospital-project/creacion de datos/isbm", methods=['GET', 'POST'])
def creation_personal_isbm():
    form = PersonalForm()
    form.hospital.choices = [hospital.hospital for hospital in Hospitales.query.all()]
    if request.method == 'POST':
        
        profesion = request.form['profesion'] if request.form['profesion'] else NaN
        especialidad = request.form['especialidad'] if request.form['especialidad'] else NaN
        sub_especialidad = request.form['sub_especialidad'] if request.form['sub_especialidad'] else NaN
        hospital = request.form['hospital'] if request.form['hospital'] else NaN

        new_idP = Personal_isbm(nombre=request.form['nombre'], profesion=profesion, n_junta=int(request.form['n_junta']), especialidad=especialidad, sub_especialidad=sub_especialidad, cargo=request.form['cargo'], correo=request.form['correo'], password=int(request.form['password']), hospital=hospital)
        session.add(new_idP)
        session.commit()

        #Updating id_jerarquico
        personal = Personal_isbm.query.filter_by(n_junta=request.form['n_junta']).first()
        if request.form['cargo'].endswith('SS'):
            personal.id_jerarquico = '1'
        elif request.form['cargo'].endswith('al'):
            personal.id_jerarquico = '2-' + str(personal.id)
        elif request.form['cargo'] == 'Supervisor':
            personal.id_jerarquico = '3-' + str(personal.id)
        elif request.form['cargo'] == 'Coordinador':
            personal.id_jerarquico = '4-1-' + str(personal.id)
        elif request.form['cargo'] == 'Medico Proveedor':
            personal.id_jerarquico = '4-2-' + str(personal.id)
        elif request.form['cargo'] == 'Establecimiento Proveedor':
            personal.id_jerarquico = '4-3-' + str(personal.id)
        else:
            personal.id_jerarquico = '5-' + str(personal.id)

        session.add(personal)
        session.commit() 

        if request.files['fys']:
            personal_id = Personal_isbm.query.filter_by(n_junta=request.form['n_junta']).first()
            new_fys = FirmasySellos(personal_id=personal_id.id, fys=request.files['fys'].read())
            session.add(new_fys)
            session.commit()
        flash("Los Datos fueron agregados con exito!")
        return render_template('personal_isbm_creation.html', form=form)
    
    else:
        return render_template('personal_isbm_creation.html', form=form)


@app.route("/hospital-project/creacion de datos/pacientes", methods=['GET', 'POST'])
def creation_pacientes():
    form = PacienteForm()
    if request.method == 'POST':
        tipo_afiliacion = request.form['tipo_afiliacion'] if request.form['tipo_afiliacion'] else NaN
        estado = request.form['estado'] if request.form['estado'] else NaN
        new_pacientes = Pacientes(n_afiliacion=request.form['n_afiliacion'], tipo_afiliacion = tipo_afiliacion, estado=estado, nombre=request.form['nombre'], password=request.form['password'], correo=request.form['correo'], edad=request.form['edad'], sexo=request.form['sexo'], dui=request.form['dui'])
        session.add(new_pacientes)
        session.commit()
        flash("Los Datos fueron agregados con exito!")
        return render_template('pacientes_creation.html', form=form)
    
    else:
        return render_template('pacientes_creation.html', form=form)


@app.route('/hospital-project/inicio de sesion', methods=['GET', 'POST'])
def inicio_de_sesion():
    form = InicioSesion()
    if request.method == 'POST':
        return redirect(url_for('SS_superior_inicio_page'))
    else:
        return render_template('inicio_de_sesion.html', form=form)


@app.route('/hospital-project/inicio de sesion/SS_Superior_inicio_page', methods=['GET', 'POST'])
def SS_superior_inicio_page():
    return render_template('SS_superior_inicio_page.html')
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
