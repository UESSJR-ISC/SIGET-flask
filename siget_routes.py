from math import ceil

from datetime import date

from werkzeug.utils import secure_filename

from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from flask import flash

from sqlalchemy import or_
from sqlalchemy import and_

from database import DB_PATH
from database import db_session

import siget_models

from server_config import *
from server_utils import *
from server import app


def get_session_type():
    return session.get('type', None)


def get_user_from_session():
    user_id = session.get('user_id', None)

    if user_id:
        return db_session.query(siget_models.Usuarios).get(user_id)
    
    return None

def allow_empty_field(value):
    if not value:
        return ''
    
    return value


@app.route('/')
def root():
    return redirect(url_for('home'))


@app.route('/siget', methods=['GET', 'POST'])
def home():
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('info'))
    
    session_user = get_user_from_session()

    if request.method == 'POST':
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        domicilio = request.form['domicilio']
        curp = request.form['curp']
        telefono = request.form['telefono']
        correo = request.form['correo']
        sexo = request.form['sexo']
        estatus = request.form['estatus']
        modalidad_id = request.form['modalidad_id']
        generacion_id = request.form['generacion_id']
        comentarios = allow_empty_field(request.form['comentarios'])
        foto = 'default.png'

        titulacion_fecha = allow_empty_field(request.form['titulacion-fecha'])
        proyecto_escrito_titulo = allow_empty_field(request.form['proyecto-escrito-titulo'])
        titulacion_presidente_nombre = allow_empty_field(request.form['titulacion-presidente-nombre'])
        titulacion_presidente_cedula = allow_empty_field(request.form['titulacion-presidente-cedula'])
        titulacion_secretario_nombre = allow_empty_field(request.form['titulacion-secretario-nombre'])
        titulacion_secretario_cedula = allow_empty_field(request.form['titulacion-secretario-cedula'])
        titulacion_vocal_nombre = allow_empty_field(request.form['titulacion-vocal-nombre'])
        titulacion_vocal_cedula = allow_empty_field(request.form['titulacion-vocal-cedula'])
        titulacion_suplente_nombre = allow_empty_field(request.form['titulacion-suplente-nombre'])
        titulacion_suplente_cedula = allow_empty_field(request.form['titulacion-suplente-cedula'])
        comite_presidente_nombre = allow_empty_field(request.form['comite-presidente-nombre'])
        comite_presidente_cedula = allow_empty_field(request.form['comite-presidente-cedula'])
        comite_secretario_nombre = allow_empty_field(request.form['comite-secretario-nombre'])
        comite_secretario_cedula = allow_empty_field(request.form['comite-secretario-cedula'])
        comite_vocal_nombre = allow_empty_field(request.form['comite-vocal-nombre'])
        comite_vocal_cedula = allow_empty_field(request.form['comite-vocal-cedula'])

        if not matricula or matricula == '':
            flash('Error: Se debe registrar una matricula.')
            return redirect(url_for('home'))
        
        egresado = db_session.query(siget_models.Egresados)\
            .filter(siget_models.Egresados.matricula==matricula)\
            .first()
        
        if egresado:
            flash('Error: La matricula ya esta registrada.')
            return redirect(url_for('home'))
        
        if not nombre or nombre == '':
            flash('Error: Se debe registrar un nombre.')
            return redirect(url_for('home'))
        
        if not apellidos or apellidos == '':
            flash('Error: Se debe registrar los apellidos.')
            return redirect(url_for('home'))

        if not domicilio or domicilio == '':
            domicilio = 'DESCONOCIDO'
        
        if not curp or curp == '':
            curp = 'DESCONOCIDO'
        
        if not telefono or telefono == '':
            telefono = 'DESCONOCIDO'

        if not correo or correo == '':
            correo = 'DESCONOCIDO'
        
        if not sexo or sexo == '':
            flash('Error: Se debe registrar un sexo.')
            return redirect(url_for('home'))
        
        if not estatus or estatus == '':
            flash('Error: Se debe registrar un estatus.')
            return redirect(url_for('home'))
        
        if not modalidad_id or modalidad_id == '':
            flash('Error: Se debe registrar una modalidad.')
            return redirect(url_for('home'))
        
        if not generacion_id or generacion_id == '':
            flash('Error: Se debe registrar una generacion.')
            return redirect(url_for('home'))

        if 'foto' in request.files and request.files['foto'].filename != '':
            foto_file = request.files['foto']

            if not validate_file_type(foto_file.filename, ALLOWED_IMAGE_TYPES):
                flash('Error: Tipo de archivo invalido.')
                return redirect(url_for('home'))
            
            foto  = save_picture(foto_file, FOTOS_EGRESADOS, True)
        
        nuevo_egresado = siget_models.Egresados()

        nuevo_egresado.matricula = matricula
        nuevo_egresado.nombre = nombre
        nuevo_egresado.apellidos = apellidos
        nuevo_egresado.domicilio = domicilio
        nuevo_egresado.curp = curp
        nuevo_egresado.telefono = telefono
        nuevo_egresado.correo = correo
        nuevo_egresado.sexo = sexo
        nuevo_egresado.estatus = estatus
        nuevo_egresado.modalidad_id = modalidad_id
        nuevo_egresado.generacion_id = generacion_id
        nuevo_egresado.comentarios = comentarios
        nuevo_egresado.foto = foto
        nuevo_egresado.unidad_id = session_user.unidad_id
        nuevo_egresado.carrera_id = session_user.carrera_id
        nuevo_egresado.titulacion_fecha = titulacion_fecha
        nuevo_egresado.proyecto_escrito_titulo = proyecto_escrito_titulo
        nuevo_egresado.titulacion_presidente_nombre = titulacion_presidente_nombre
        nuevo_egresado.titulacion_presidente_cedula = titulacion_presidente_cedula
        nuevo_egresado.titulacion_secretario_nombre = titulacion_secretario_nombre
        nuevo_egresado.titulacion_secretario_cedula = titulacion_secretario_cedula
        nuevo_egresado.titulacion_vocal_nombre = titulacion_vocal_nombre
        nuevo_egresado.titulacion_vocal_cedula = titulacion_vocal_cedula
        nuevo_egresado.titulacion_suplente_nombre = titulacion_suplente_nombre
        nuevo_egresado.titulacion_suplente_cedula = titulacion_suplente_cedula
        nuevo_egresado.comite_presidente_nombre = comite_presidente_nombre
        nuevo_egresado.comite_presidente_cedula = comite_presidente_cedula
        nuevo_egresado.comite_secretario_nombre = comite_secretario_nombre
        nuevo_egresado.comite_secretario_cedula = comite_secretario_cedula
        nuevo_egresado.comite_vocal_nombre = comite_vocal_nombre
        nuevo_egresado.comite_vocal_cedula = comite_vocal_cedula

        db_session.add(nuevo_egresado)
        db_session.commit()

        flash(f'Info: Egresado {nuevo_egresado.nombre} registrado correctamente.')
        return redirect(url_for('home', include=nuevo_egresado.id, _anchor=f'popup/modal-egresado-{nuevo_egresado.id}'))

    egresados = db_session.query(siget_models.Egresados)

    busqueda = request.args.get('buscar')
    
    if busqueda and busqueda != '':
        egresados = egresados.filter(or_(
            siget_models.Egresados.nombre.like(f'%{busqueda}%'),
            siget_models.Egresados.apellidos.like(f'%{busqueda}%'),
            siget_models.Egresados.domicilio.like(f'%{busqueda}%'),
            siget_models.Egresados.correo.like(f'%{busqueda}%'),
            siget_models.Egresados.telefono.like(f'%{busqueda}%'),
            siget_models.Egresados.curp.like(f'%{busqueda}%')
        ))
    
    generacion = request.args.get('generacion')

    if generacion and generacion != '' and generacion != 'all':
        egresados = egresados.filter(siget_models.Egresados.generacion_id==generacion)

    modalidad = request.args.get('modalidad')

    if modalidad and modalidad != '' and modalidad != 'all':
        egresados = egresados.filter(siget_models.Egresados.modalidad_id==modalidad)
    
    estatus = request.args.get('estatus')

    if estatus and estatus != '' and estatus != 'all':
        egresados = egresados.filter(siget_models.Egresados.estatus==estatus)

    unidad = request.args.get('unidad')

    if unidad and unidad != '' and unidad != 'all':
        egresados = egresados.filter(siget_models.Egresados.unidad_id==unidad)
    
    carrera = request.args.get('carrera')

    if carrera and carrera != '' and carrera != 'all':
        egresados = egresados.filter(siget_models.Egresados.carrera_id==carrera)

    generaciones = db_session.query(siget_models.Generaciones)

    if session_type == 'user':
        egresados = egresados.filter(
            and_(
                siget_models.Egresados.unidad_id==session_user.unidad_id,
                siget_models.Egresados.carrera_id==session_user.carrera_id
            )
        )

        generaciones = generaciones.filter(
            and_(
                siget_models.Generaciones.unidad_id==session_user.unidad_id,
                siget_models.Generaciones.carrera_id==session_user.carrera_id
            )
        )
    
    elif session_type == 'coordi' or session_type == 'control':
        egresados = egresados.filter(
            siget_models.Egresados.unidad_id==session_user.unidad_id
        )

        generaciones = generaciones.filter(
            siget_models.Generaciones.unidad_id==session_user.unidad_id
        )
    
    if generaciones.count() == 0 and (session_type != 'admin' or session_type != 'root'):
        flash("Info: Antes de poder registrar egresados, registra las generaciones de esta carrera en esta UES.")
        return redirect(url_for('generaciones'))

    sort = request.args.get('sort')
    order = request.args.get('order')

    if sort and sort == 'nombre':
        if order and order == 'asc':
            egresados = egresados.order_by(siget_models.Egresados.nombre.asc())
        else:
            egresados = egresados.order_by(siget_models.Egresados.nombre.desc())
    
    elif sort and sort == 'apellidos':
        if order and order == 'asc':
            egresados = egresados.order_by(siget_models.Egresados.apellidos.asc())
        else:
            egresados = egresados.order_by(siget_models.Egresados.apellidos.desc())
    
    elif sort and sort == 'modalidad':
        if order and order == 'asc':
            egresados = egresados.join(siget_models.Modalidades).order_by(siget_models.Modalidades.nombre.asc())
        else:
            egresados = egresados.join(siget_models.Modalidades).order_by(siget_models.Modalidades.nombre.desc())
    
    elif sort and sort == 'estatus':
        if order and order == 'asc':
            egresados = egresados.order_by(siget_models.Egresados.estatus.asc())
        else:
            egresados = egresados.order_by(siget_models.Egresados.estatus.desc())
    
    elif sort and sort == 'generacion':
        if order and order == 'asc':
            egresados = egresados.join(siget_models.Generaciones).order_by(siget_models.Generaciones.anio_inicio.asc())
        
    else:
        egresados = egresados.join(siget_models.Generaciones).order_by(siget_models.Generaciones.anio_inicio.desc())
    
    page = request.args.get('page')
    page = int(page) if (page and page != '') else 1

    page_size = 6
    pages_count = ceil(egresados.count() / page_size)

    page_offset = (page - 1) * page_size
    page_limit = page_offset + page_size
    
    egresados = egresados.slice(page_offset, page_limit)

    egresados = egresados.all()
    include = request.args.get('include')

    if include and include != '':
        include = db_session.query(siget_models.Egresados).get(include)

        if include and not include in egresados:
            egresados.insert(0, include)

    generaciones = generaciones.all()
    modalidades = db_session.query(siget_models.Modalidades).all()

    unidades = []
    carreras = []

    if session_type == 'admin':
        unidades = db_session.query(siget_models.Unidades).all()
    
    if session_type != 'user':
        carreras = db_session.query(siget_models.Carreras).all()

    return render_template('siget/home.html',
        generaciones=generaciones,
        modalidades=modalidades,
        egresados=egresados,
        page=page,
        page_size=page_size,
        pages_count=pages_count,
        session_type=session_type,
        session_user=session_user,
        unidades=unidades,
        carreras=carreras,
        args=request.args.to_dict())

@app.post('/siget/egresado/<id>/file')
def egresados_addfile(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresado = db_session.query(siget_models.Egresados).get(id)

    if not egresado:
        flash('Error: Egresado no encontrado.')
        return redirect(url_for('home'))
    
    if session_type != 'admin':
        if egresado.unidad_id != session_user.unidad_id or egresado.carrera_id != session_user.carrera_id:
            flash('Error: No tienes permiso para editar este usuario.')
            return redirect(url_for('home'))

    if not 'fichero' in request.files or request.files['fichero'].filename == '':
        flash("Error: Debes adjuntar un archivo.")
        return redirect(url_for('home'))

    fichero_file = request.files['fichero']

    if not validate_file_type(fichero_file.filename, ALLOWED_DOC_TYPES):
        flash('Error: Tipo de archivo invalido.')
        return redirect(url_for('home'))
    
    ruta = save_file(fichero_file, FICHEROS_ADJUNTOS)

    nuevo_fichero = siget_models.Ficheros()

    nuevo_fichero.ruta = ruta
    nuevo_fichero.nombre = secure_filename(fichero_file.filename)
    nuevo_fichero.egresado_id = egresado.id

    db_session.add(nuevo_fichero)
    db_session.commit()

    flash(f'Info: El fichero {nuevo_fichero.nombre} se adjunto correctamente a {egresado.nombre}')
    return redirect(url_for('home', include=egresado.id, _anchor=f'popup/modal-egresado-{egresado.id}'))

@app.get('/siget/egresado/file/<id>/delete')
def egresado_delfile(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    fichero = db_session.query(siget_models.Ficheros).get(id)

    if not fichero:
        flash('Error: El fichero no existe.')
        return redirect(url_for('home'))
    
    if session_type != 'admin':
        if fichero.egresado.unidad_id != session_user.unidad_id or fichero.egresado.carrera_id != session_user.carrera_id:
            flash('Error: No tienes permiso para eliminar este archivo.')
            return redirect(url_for('home'))
    
    os.remove(FICHEROS_ADJUNTOS + fichero.ruta)
    
    db_session.delete(fichero)
    db_session.commit()

    flash('El fichero adjunto se elimino correctamente.')
    return redirect(url_for('home', include=fichero.egresado.id, _anchor=f'popup/modal-egresado-{fichero.egresado.id}'))

@app.get('/siget/egresados/<id>/delete')
def egresados_delete(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresado = db_session.query(siget_models.Egresados).get(id)

    if not egresado:
        flash('Error: Egresado no encontrado.')
        return redirect(url_for('home'))
    
    if session_type != 'admin':
        if egresado.unidad_id != session_user.unidad_id or egresado.carrera_id != session_user.carrera_id:
            flash('Error: No tienes permiso para editar este usuario.')
            return redirect(url_for('home'))
    
    if egresado.foto != 'default.png':
        os.remove(FOTOS_EGRESADOS + egresado.foto)
    
    db_session.delete(egresado)
    db_session.commit()

    flash('Info: Egresado eliminado correctamente.')
    return redirect(url_for('home'))

@app.post('/siget/egresados/<id>/update')
def egresados_update(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresado = db_session.query(siget_models.Egresados).get(id)

    if not egresado:
        flash('Error: Egresado no encontrado.')
        return redirect(url_for('home'))
    
    if session_type != 'admin':
        if egresado.unidad_id != session_user.unidad_id or egresado.carrera_id != session_user.carrera_id:
            flash('Error: No tienes permiso para editar este usuario.')
            return redirect(url_for('home'))
    
    matricula = request.form['matricula']
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    domicilio = request.form['domicilio']
    curp = request.form['curp']
    telefono = request.form['telefono']
    correo = request.form['correo']
    sexo = request.form['sexo']
    estatus = request.form['estatus']
    modalidad_id = request.form['modalidad_id']
    generacion_id = request.form['generacion_id']
    comentarios = request.form['comentarios']

    titulacion_fecha = request.form['titulacion-fecha']

    titulacion_presidente_nombre = request.form['titulacion-presidente-nombre']
    titulacion_presidente_cedula = request.form['titulacion-presidente-cedula']
    titulacion_secretario_nombre = request.form['titulacion-secretario-nombre']
    titulacion_secretario_cedula = request.form['titulacion-secretario-cedula']
    titulacion_vocal_nombre = request.form['titulacion-vocal-nombre']
    titulacion_vocal_cedula = request.form['titulacion-vocal-cedula']
    titulacion_suplente_nombre = request.form['titulacion-suplente-nombre']
    titulacion_suplente_cedula = request.form['titulacion-suplente-cedula']

    comite_presidente_nombre = request.form['comite-presidente-nombre']
    comite_presidente_cedula = request.form['comite-presidente-cedula']
    comite_secretario_nombre = request.form['comite-secretario-nombre']
    comite_secretario_cedula = request.form['comite-secretario-cedula']
    comite_vocal_nombre = request.form['comite-vocal-nombre']
    comite_vocal_cedula = request.form['comite-vocal-cedula']

    proyecto_escrito_titulo = request.form['proyecto-escrito-titulo']

    if matricula and matricula != '':
        egresado_check = db_session.query(siget_models.Egresados)\
            .filter(siget_models.Egresados.matricula==matricula)\
            .first()
        
        if egresado_check:
            flash(f'Error: La matricula {matricula} ya esta registrada.')
            return redirect(url_for('home'))

        egresado.matricula = matricula
    
    if titulacion_fecha and titulacion_fecha != '':
        egresado.titulacion_fecha = titulacion_fecha
    
    if titulacion_presidente_nombre and titulacion_presidente_nombre != '':
        egresado.titulacion_presidente_nombre = titulacion_presidente_nombre
    
    if titulacion_presidente_cedula and titulacion_presidente_cedula != '':
        egresado.titulacion_presidente_cedula = titulacion_presidente_cedula
    
    if titulacion_secretario_nombre and titulacion_secretario_nombre != '':
        egresado.titulacion_secretario_nombre = titulacion_secretario_nombre
        
    if titulacion_secretario_cedula and titulacion_secretario_cedula != '':
        egresado.titulacion_secretario_cedula = titulacion_secretario_cedula
    
    if titulacion_vocal_nombre and titulacion_vocal_nombre != '':
        egresado.titulacion_vocal_nombre = titulacion_vocal_nombre
    
    if titulacion_vocal_cedula and titulacion_vocal_cedula != '':
        egresado.titulacion_vocal_cedula = titulacion_vocal_cedula
    
    if titulacion_suplente_nombre and titulacion_suplente_nombre != '':
        egresado.titulacion_suplente_nombre = titulacion_suplente_nombre
    
    if titulacion_suplente_cedula and titulacion_suplente_cedula != '':
        egresado.titulacion_suplente_cedula = titulacion_suplente_cedula
    
    if comite_presidente_nombre and comite_presidente_nombre != '':
        egresado.comite_presidente_nombre = comite_presidente_nombre
    
    if comite_presidente_cedula and comite_presidente_cedula != '':
        egresado.comite_presidente_cedula = comite_presidente_cedula
    
    if comite_secretario_nombre and comite_secretario_nombre != '':
        egresado.comite_secretario_nombre = comite_secretario_nombre
    
    if comite_secretario_cedula and comite_secretario_cedula != '':
        egresado.comite_secretario_cedula = comite_secretario_cedula
    
    if comite_vocal_nombre and comite_vocal_nombre != '':
        egresado.comite_vocal_nombre = comite_vocal_nombre
    
    if comite_vocal_cedula and comite_vocal_cedula != '':
        egresado.comite_vocal_cedula = comite_vocal_cedula
    
    if proyecto_escrito_titulo and proyecto_escrito_titulo != '':
        egresado.proyecto_escrito_titulo = proyecto_escrito_titulo

    if nombre and nombre != '':
        egresado.nombre = nombre
    
    if apellidos and apellidos != '':
        egresado.apellidos = apellidos

    if domicilio and domicilio != '':
        egresado.domicilio = domicilio
    
    if curp and curp != '':
        egresado.curp = curp
    
    if telefono and telefono != '':
        egresado.telefono = telefono

    if correo and correo != '':
        egresado.correo = correo
    
    if sexo and sexo != '':
        egresado.sexo = sexo
    
    if estatus and estatus != '':
        egresado.estatus = estatus
    
    if modalidad_id and modalidad_id != '':
        egresado.modalidad_id = modalidad_id
    
    if generacion_id and generacion_id == '':
        egresado.generacion_id = generacion_id
    
    if comentarios and comentarios != '':
        egresado.comentarios = comentarios

    if 'foto' in request.files and request.files['foto'].filename != '':
        foto_file = request.files['foto']

        if not validate_file_type(foto_file.filename, ALLOWED_IMAGE_TYPES):
            flash('Error: Tipo de archivo invalido.')
            return redirect(url_for('home'))
        
        if egresado.foto != 'default.png':
            os.remove(FOTOS_EGRESADOS + egresado.foto)
        
        egresado.foto  = save_picture(foto_file, FOTOS_EGRESADOS, True)
    
    db_session.add(egresado)
    db_session.commit()

    flash(f'Info: Egresado {egresado.nombre} actualizado correctamente.')
    return redirect(url_for('home', include=egresado.id, _anchor=f'popup/modal-egresado-{egresado.id}'))

@app.post('/siget/generaciones/<id>/update')
def generaciones_update(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    generacion = db_session.query(siget_models.Generaciones).get(id)

    if not generacion:
        flash('Error: Generacion no encontrada.')
        return redirect(url_for('generaciones'))
    
    if session_type != 'admin':
        if generacion.unidad_id != session_user.unidad_id or generacion.carrera_id != session_user.carrera_id:
            flash('Error: No tienes permiso para editar esta generacion.')
            return redirect(url_for('home'))
    
    anio_inicio = request.form['anio_inicio']
    anio_final = request.form['anio_final']
    
    if 'foto' in request.files and request.files['foto'].filename != '':
        foto_file = request.files['foto']

        if not validate_file_type(foto_file.filename, ALLOWED_IMAGE_TYPES):
            flash('Error: Tipo de archivo invalido.')
            return redirect(url_for('generaciones'))

        if generacion.foto != 'default.png':
            os.remove(FOTOS_GENERACIONALES + generacion.foto)
        
        generacion.foto  = save_picture(foto_file, FOTOS_GENERACIONALES)

    if anio_inicio and anio_inicio != '':
        generacion.anio_inicio = anio_inicio
    
    if anio_final and anio_final != '':
        generacion.anio_final = anio_final

    db_session.add(generacion)
    db_session.commit()

    flash('Info: Generacion actualizada correctamente.')
    return redirect(url_for('generaciones'))

@app.get('/siget/generaciones/<id>/delete')
def generaciones_delete(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    generacion = db_session.query(siget_models.Generaciones).get(id)

    if not generacion:
        flash('Error: Generacion no encontrada.')
        return redirect(url_for('generaciones'))
    
    if session_type != 'admin':
        if generacion.unidad_id != session_user.unidad_id or generacion.carrera_id != session_user.carrera_id:
            flash('Error: No tienes permiso para editar esta generacion.')
            return redirect(url_for('home'))
    
    if generacion.foto != 'default.png':
        os.remove(FOTOS_GENERACIONALES + generacion.foto)
    
    db_session.delete(generacion)
    db_session.commit()

    flash('Info: Generacion eliminada correctamente.')
    return redirect(url_for('generaciones'))

@app.route('/siget/generaciones', methods=['GET', 'POST'])
def generaciones():
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    if request.method == 'POST':
        foto = 'default.png'
        anio_inicio = request.form['anio_inicio']
        anio_final = request.form['anio_final']
        
        if 'foto' in request.files and request.files['foto'].filename != '':
            foto_file = request.files['foto']

            if not validate_file_type(foto_file.filename, ALLOWED_IMAGE_TYPES):
                flash('Error: Tipo de archivo invalido.')
                return redirect(url_for('generaciones'))
            
            foto = save_picture(foto_file, FOTOS_GENERACIONALES)

        if not anio_inicio or anio_inicio == '':
            flash('Error: No se proporciono el año de ingreso.')
            return redirect(url_for('generaciones'))
        
        if not anio_final or anio_final == '':
            flash('Error: No se proporciono el año de egreso.')
            return redirect(url_for('generaciones'))
        
        nueva_generacion = siget_models.Generaciones()

        nueva_generacion.anio_inicio = anio_inicio
        nueva_generacion.anio_final = anio_final
        nueva_generacion.foto = foto
        nueva_generacion.unidad_id = session_user.unidad_id
        nueva_generacion.carrera_id = session_user.carrera_id

        db_session.add(nueva_generacion)
        db_session.commit()

    generaciones = db_session.query(siget_models.Generaciones)

    if session_type == 'user':
        generaciones = generaciones.filter(
            and_(
                siget_models.Generaciones.unidad_id==session_user.unidad_id,
                siget_models.Generaciones.carrera_id==session_user.carrera_id
            )
        )

    generaciones = generaciones.all()

    return render_template('siget/generaciones.html',
        generaciones=generaciones,
        session_type=session_type,
        session_user=session_user)

@app.get('/siget/reportes')
def reportes():
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresados = db_session.query(siget_models.Egresados)
    generaciones = db_session.query(siget_models.Generaciones)

    if session_type == 'user':
        egresados = egresados.filter(
            and_(
                siget_models.Egresados.unidad_id==session_user.unidad_id,
                siget_models.Egresados.carrera_id==session_user.carrera_id
            )
        )

        generaciones = generaciones.filter(
            and_(
                siget_models.Generaciones.unidad_id==session_user.unidad_id,
                siget_models.Generaciones.carrera_id==session_user.carrera_id
            )
        )
    
    elif session_type == 'coordi' or session_type == 'control':
        egresados = egresados.filter(
            siget_models.Egresados.unidad_id==session_user.unidad_id
        )

        generaciones = generaciones.filter(
            siget_models.Generaciones.unidad_id==session_user.unidad_id
        )
    
    generaciones = generaciones.all()

    return render_template('siget/reportes.html',
        generaciones=generaciones,
        egresados=egresados,
        models=siget_models,
        and_=and_,
        session_type=session_type,
        session_user=session_user,
        fecha_de_reporte=date.today())


@app.route('/siget/admin/database', methods=['GET', 'POST'])
def admin_database():
    session_type = get_session_type()

    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()

    if request.method == 'POST':
        return

    db_file = {
        'name': DB_PATH
    }
    
    if os.path.exists(DB_PATH):
        db_download = True
    else:
        db_download = False
    
    return render_template('siget/admin.html',
        active='database',
        db_download=db_download,
        db_file=db_file,
        session_type=session_type,
        session_user=session_user)


@app.route('/siget/admin/unidades', methods=['GET', 'POST'])
def admin_unidades():
    session_type = get_session_type()

    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))

    session_user = get_user_from_session()
    
    if request.method == 'POST':
        nombre = request.form['nombre']

        if not nombre or nombre == '':
            flash('Error: Debes indicar un nombre.')
            return redirect(url_for('admin_unidades'))
        
        nueva_unidad = siget_models.Unidades()

        nueva_unidad.nombre = nombre

        db_session.add(nueva_unidad)
        db_session.commit()

    unidades = db_session.query(siget_models.Unidades).all()
    
    return render_template('siget/admin.html',
        active='unidades',
        unidades=unidades,
        session_type=session_type,
        session_user=session_user)

@app.get('/siget/admin/unidades/<id>/delete')
def admin_unidades_delete(id):
    session_type = get_session_type()

    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    unidad = db_session.query(siget_models.Unidades).get(id)

    if not unidad:
        flash('Error: Unidad no encontrada.')
        return redirect(url_for('admin_unidades'))
    
    db_session.delete(unidad)
    db_session.commit()

    flash('Info: Unidad eliminada correctamente.')
    return redirect(url_for('admin_unidades'))

@app.post('/siget/admin/unidades/<id>/update')
def admin_unidades_update(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    unidad = db_session.query(siget_models.Unidades).get(id)

    if not unidad:
        flash('Error: Unidad no encontrada.')
        return redirect(url_for('admin_unidades'))
    
    nombre = request.form['nombre']

    if nombre and nombre != '':
        flash('Info: unidad actualizada correctamente.')
        unidad.nombre = nombre
    
    db_session.add(unidad)
    db_session.commit()

    return redirect(url_for('admin_unidades'))

@app.route('/siget/admin/carreras', methods=['GET', 'POST'])
def admin_carreras():
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    if request.method == 'POST':
        nombre = request.form['nombre']

        if not nombre or nombre == '':
            flash('Error: Indica el nombre de la carrera.')
            return redirect(url_for('admin_carreras'))
        
        nueva_carrera = siget_models.Carreras()

        nueva_carrera.nombre = nombre

        db_session.add(nueva_carrera)
        db_session.commit()
    
    carreras = db_session.query(siget_models.Carreras).all()
    return render_template('siget/admin.html',
        active='carreras',
        carreras=carreras,
        session_type=session_type,
        session_user=session_user)

@app.get('/siget/admin/carreras/<id>/delete')
def admin_carreras_delete(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    carrera = db_session.query(siget_models.Carreras).get(id)

    if not carrera:
        flash('Error: Carrera no encontrada.')
        return redirect(url_for('admin_carreras'))
    
    db_session.delete(carrera)
    db_session.commit()

    flash('Info: Carrera eliminada correctamente.')
    return redirect(url_for('admin_carreras'))

@app.post('/siget/admin/carreras/<id>/update')
def admin_carreras_update(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    carrera = db_session.query(siget_models.Carreras).get(id)

    if not carrera:
        flash('Error: Carrera no encontrada.')
        return redirect(url_for('admin_carreras'))
    
    nombre = request.form['nombre']

    if nombre and nombre != '':
        carrera.nombre = nombre
    
    db_session.add(carrera)
    db_session.commit()

    flash('Info: Carrera actualizada correctamente.')
    return redirect(url_for('admin_carreras'))

@app.get('/siget/admin/modalidades/<id>/delete')
def modalidades_delete(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    modalidad = db_session.query(siget_models.Modalidades).get(id)

    if not modalidad:
        flash('Error: Modalidad no encontrada.')
        return redirect(url_for('modalidades'))
    
    if modalidad.manual != 'default.pdf':
        os.remove(MANUALES_MODALIDADES + modalidad.manual)
    
    db_session.delete(modalidad)
    db_session.commit()

    flash('Info: Modalidad eliminada correctamente.')
    return redirect(url_for('modalidades'))

@app.post('/siget/admin/modalidades/<id>/update')
def modalidades_update(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    modalidad = db_session.query(siget_models.Modalidades).get(id)

    if not modalidad:
        flash('Error: Modalidad no encontrada.')
        return redirect(url_for(('modalidades')))

    if 'manual' in request.files and request.files['manual'].filename != '':
        manual_file = request.files['manual']

        if not validate_file_type(manual_file.filename, ALLOWED_DOC_TYPES):
            flash('Error: Tipo de archivo invalido.')
            return redirect(url_for('modalidades'))

        if modalidad.manual != 'default.pdf':
            os.remove(MANUALES_MODALIDADES + modalidad.manual)

        modalidad.manual = save_file(manual_file, MANUALES_MODALIDADES)
    
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']

    if nombre and nombre != '':
        modalidad.nombre = nombre
    
    if descripcion and descripcion != '':
        modalidad.descripcion = descripcion
    
    db_session.add(modalidad)
    db_session.commit()

    flash(f'Info: Modalidad {modalidad.nombre} actualizada correctamente.')
    return redirect(url_for('modalidades'))

@app.route('/siget/admin/modalidades', methods=['GET', 'POST'])
def modalidades():
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    if request.method == 'POST':
        manual = 'default.pdf'
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        if 'manual' in request.files and request.files['manual'].filename != '':
            manual_file = request.files['manual']

            if not validate_file_type(manual_file.filename, ALLOWED_DOC_TYPES):
                flash('Error: Tipo de archivo invalido.')
                return redirect(url_for('modalidades'))
            
            manual = save_file(manual_file, MANUALES_MODALIDADES)

        if not nombre or nombre == '':
            flash('Error: No se proporciono el nombre de la modalidad.')
            return redirect(url_for('modalidades'))
        
        if not descripcion or descripcion == '':
            flash('Error: No se proporciono la descripcion de la modalidad.')
            return redirect(url_for('modalidades'))
        
        nueva_modalidad = siget_models.Modalidades()

        nueva_modalidad.manual = manual
        nueva_modalidad.nombre = nombre
        nueva_modalidad.descripcion = descripcion

        db_session.add(nueva_modalidad)
        db_session.commit()

    modalidades = db_session.query(siget_models.Modalidades)

    return render_template('siget/admin.html',
        active='modalidades',
        modalidades=modalidades,
        session_type=session_type,
        session_user=session_user)

@app.get('/siget/admin/usuarios')
def admin_usuarios():
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    unidades = db_session.query(siget_models.Unidades).all()
    carreras = db_session.query(siget_models.Carreras).all()
    usuarios = db_session.query(siget_models.Usuarios).all()

    return render_template('siget/admin.html',
        active='usuarios',
        unidades=unidades,
        carreras=carreras,
        usuarios=usuarios,
        session_type=session_type,
        session_user=session_user)

@app.post('/siget/usuario')
def usuario_post():
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    matricula = request.form['matricula']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido-paterno']
    apellido_materno = request.form['apellido-materno']
    unidad_id = request.form['unidad-id']
    carrera_id = request.form['carrera-id']
    rol = request.form['rol']

    if not matricula or matricula == '':
        flash('Error: Se debe indicar una matricula.')
        return redirect(url_for('admin_usuarios'))
    
    check_usuario = db_session.query(siget_models.Usuarios).filter(siget_models.Usuarios.matricula==matricula).first()

    if check_usuario:
        flash('Error: La matricula ya esta registrada.')
        return redirect(url_for('admin_usuarios'))
    
    if not nombre or nombre == '':
        flash('Error: Debes proporcionar un nombre.')
        return redirect(url_for('admin_usuarios'))
    
    if not apellido_paterno or apellido_paterno == '':
        flash('Error: Debes indicar el apellido paterno.')
        return redirect(url_for('admin_usuarios'))
    
    if not apellido_materno:
        apellido_materno = ''
    
    if not unidad_id or unidad_id == '':
        flash('Error: Se debe seleccionar una UES.')
        return redirect(url_for('admin_usuarios'))
    
    if not carrera_id or carrera_id == '':
        flash('Error: Se debe seleccionar una carrera.')
        return redirect(url_for('admin_usuarios'))

    if not rol or rol == '':
        flash('Error: Se debe seleccionar un rol.')
        return redirect(url_for('admin_usuarios'))
    
    nuevo_usuario = siget_models.Usuarios()

    nuevo_usuario.matricula = matricula
    nuevo_usuario.nombre = nombre
    nuevo_usuario.apellido_paterno = apellido_paterno
    nuevo_usuario.apellido_materno = apellido_materno
    nuevo_usuario.clave = matricula
    nuevo_usuario.unidad_id = unidad_id
    nuevo_usuario.carrera_id = carrera_id
    nuevo_usuario.rol = rol

    db_session.add(nuevo_usuario)
    db_session.commit()

    flash('Info: Usuario creado correctamente.')
    return redirect(url_for('admin_usuarios'))

@app.get('/siget/usuario/<id>/delete')
def usuario_delete(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    usuario = db_session.query(siget_models.Usuarios).get(id);

    if not usuario:
        flash('Error: Usuario no encontrado.')
        return redirect(url_for('admin_usuarios'))
    
    db_session.delete(usuario)
    db_session.commit()

    flash('Info: Usuario eliminado correctamente.')
    return redirect(url_for('admin_usuarios'))

@app.get('/siget/usuario/<id>/reset')
def usuario_reset(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    usuario = db_session.query(siget_models.Usuarios).get(id);

    if not usuario:
        flash('Error: Usuario no encontrado.')
        return redirect(url_for('admin_usuarios'))
    
    usuario.clave = usuario.matricula
    
    db_session.add(usuario)
    db_session.commit()

    flash('Info: Usuario reseteado correctamente.')
    return redirect(url_for('admin_usuarios'))

@app.post('/siget/usuario/<id>/update')
def usuario_update(id):
    session_type = get_session_type()
    
    if not session_type or (session_type != 'admin' and session_type != 'root'):
        return redirect(url_for('login'))
    
    usuario = db_session.query(siget_models.Usuarios).get(id);

    if not usuario:
        flash('Error: usuario no encontrado.')
        return redirect(url_for('admin_suaurios'))
    
    matricula = request.form['matricula']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido-paterno']
    apellido_materno = request.form['apellido-materno']
    unidad_id = request.form['unidad-id']
    carrera_id = request.form['carrera-id']
    rol = request.form['rol']

    if matricula and matricula != '':
        check_usuario = db_session.query(siget_models.Usuarios).filter(siget_models.Usuarios.matricula==matricula).first()

        if check_usuario:
            flash(f'Error: La matricula {matricula} ya esta registrada.')
            return redirect(url_for('admin_usuarios'))
        
        if usuario.clave == usuario.matricula:
            usuario.clave = matricula
        
        usuario.matricula = matricula
    
    if nombre and nombre != '':
        usuario.nombre = nombre
    
    if apellido_paterno and apellido_paterno != '':
        usuario.apellido_paterno = apellido_paterno
    
    if apellido_materno and apellido_materno != '':
        usuario.apellido_materno = apellido_materno
    
    if unidad_id and unidad_id != '':
        usuario.unidad_id = unidad_id
    
    if carrera_id and carrera_id != '':
        usuario.carrera_id = carrera_id
    
    if rol and rol != '':
        usuario.rol = rol
    
    db_session.add(usuario)
    db_session.commit()

    flash(f'Info: Usuario {usuario.nombre} actualizado correctamente')
    return redirect(url_for('admin_usuarios'))

@app.route('/siget/login', methods=['GET', 'POST'])
def login():
    if get_session_type():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        matricula = request.form['matricula']
        clave = request.form['clave']

        if not matricula or matricula == '':
            flash('Error: Credenciales invalidas.')
            return redirect(url_for('login'))
        
        if not clave or clave == '':
            flash('Error: Credenciales invalidas.')
            return redirect(url_for('login'))
        
        if matricula == ADMIN_ID and clave == ADMIN_PASSW:
            session['type'] = 'root'
            return redirect(url_for('admin_unidades'))

        usuario = db_session.query(siget_models.Usuarios).filter(
            and_(
                    siget_models.Usuarios.matricula==matricula,
                    siget_models.Usuarios.clave==clave
                )
        ).first()

        if not usuario:
            flash('Error: Credenciales invalidas.')
            return redirect(url_for('login'))
        
        if usuario.rol == 3:
            session['type'] = 'user'
        
        elif usuario.rol == 2:
            session['type'] = 'control'
        
        elif usuario.rol == 1:
            session['type'] = 'coordi'
        
        elif usuario.rol == 0:
            session['type'] = 'admin'

        session['user_id'] = usuario.id
        
        if usuario.clave == usuario.matricula:
            return redirect(url_for('change_password'))
        
        if usuario.rol == 0:
            return redirect(url_for('admin_unidades'))
            
        return redirect(url_for('home'))

    return render_template('siget/login.html')

@app.get('/siget/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/siget/change/password', methods=['GET', 'POST'])
def change_password():
    session_type = get_session_type()
    session_user = get_user_from_session()

    if session_user.clave != session_user.matricula:
        return redirect(url_for('home'))

    if request.method == 'POST':
        clave = request.form['clave']
        clave_confirmar = request.form['clave-confirmar']

        if not clave or clave == '':
            flash('Error: Indica una clave valida.')
            return redirect(url_for('change_password'))
        
        if not clave_confirmar or clave_confirmar == '':
            flash('Error: Confirma la clave.')
            return redirect(url_for('change_password'))
        
        if clave != clave_confirmar:
            flash('Error: Las claves no coinciden.')
            return redirect(url_for('change_password'))
        
        if clave == session_user.clave:
            flash('Error: La clave no puede ser la misma que tu matricula.')
            return redirect(url_for('change_password'))
        
        session_user.clave = clave

        db_session.add(session_user)
        db_session.commit()

        session.clear()

        flash('Info: Se actualizo tu clave, ahora puedes iniciar sesion con ella.')
        return redirect(url_for('login'))

    return render_template('siget/change-password.html', session_user=session_user)

@app.get('/siget/info')
def info():
    session_type = get_session_type()    
    session_user = get_user_from_session()

    generaciones = db_session.query(siget_models.Generaciones).all()
    modalidades = db_session.query(siget_models.Modalidades).all()
    titulados = {}
    total_titulados = 0
    total_egresados = db_session.query(siget_models.Egresados).count()
    total_carreras = db_session.query(siget_models.Carreras).count()

    for modalidad in modalidades:
        titulados[modalidad.id] = db_session.query(siget_models.Egresados).filter(
            and_(
                siget_models.Egresados.modalidad_id==modalidad.id,
                siget_models.Egresados.estatus==3
            )
        ).count()

        total_titulados += titulados[modalidad.id]

    return render_template('siget/info.html', 
        session_type=session_type, 
        session_user=session_user,
        generaciones=generaciones,
        modalidades=modalidades,
        titulados=titulados,
        total_titulados=total_titulados,
        total_egresados=total_egresados,
        total_carreras=total_carreras)
