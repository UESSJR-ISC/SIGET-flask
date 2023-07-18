import os
import uuid

from math import ceil

from PIL import Image
from io import BytesIO

from flask import flash
from flask import url_for
from flask import request
from flask import session
from flask import redirect
from flask import render_template
from flask import Flask

from flask_session import Session

from sqlalchemy import or_
from sqlalchemy import and_

from database import Database
from database import engine
from database import db_session

from datetime import date

from werkzeug.utils import secure_filename

import models

ADMIN_ID = 'root'
ADMIN_PASSW = 'toor'

STATIC_URL_PATH = ''

if not "DOCKER" in os.environ:
    STATIC_FOLDER = 'static'

else:
    STATIC_FOLDER = '/siget-vol/static'

IMG_FOLDER = STATIC_FOLDER + '/img'

FOTOS_GENERACIONALES = IMG_FOLDER + '/generacion/'
FOTOS_EGRESADOS = IMG_FOLDER + '/egresado/'
FOTOS_BLOG = IMG_FOLDER + '/blog/'
MANUALES_MODALIDADES = STATIC_FOLDER + '/manual/'
FICHEROS_ADJUNTOS = STATIC_FOLDER + '/adjuntos/'

def check_folder_existance(path):
    if not os.path.isdir(path):
        os.makedirs(path)

check_folder_existance(STATIC_FOLDER)
check_folder_existance(IMG_FOLDER)
check_folder_existance(FOTOS_GENERACIONALES)
check_folder_existance(FOTOS_EGRESADOS)
check_folder_existance(FOTOS_BLOG)
check_folder_existance(MANUALES_MODALIDADES)
check_folder_existance(FICHEROS_ADJUNTOS)

SESSION_TYPE = 'filesystem'
SECRET_KEY = 'dmo5S4DxuD^9IWK1k33o7Xg88J&D8fq!'
ALLOWED_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
ALLOWED_DOC_TYPES = ['pdf', 'doc', 'docx']

app = Flask(__name__, static_url_path=STATIC_URL_PATH, static_folder=STATIC_FOLDER)
app.config.from_object(__name__)

Database.metadata.create_all(engine)
Session(app)

def validate_file_type(filename: str, types):
    return filename != '' and \
        '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in types


def guardar_foto(file, path, crop=False):
    image_data = file.read()
    image = Image.open(BytesIO(image_data))

    if crop:
        width, height = image.size

        crop_reference = width if width < height else height
        crop_area = (0, 0, crop_reference, crop_reference)
        
        image = image.crop(crop_area)
        image = image.resize((480, 480), Image.ANTIALIAS)

    file_name = "%s.png" % str(uuid.uuid4())
    file_path = path + file_name

    image.save(file_path, format="png")

    return file_name


def guardar_archivo(file, path):
    file_name = "%s.pdf" % str(uuid.uuid4())
    file_path = path + file_name

    file.save(file_path)

    return file_name


def get_session_type():
    return session.get('type', None)


def get_user_from_session():
    user_id = session.get('user_id', None)

    if user_id:
        return db_session.query(models.Usuarios).get(user_id)
    
    return None


@app.teardown_request
def remove_session(ex=None):
    db_session.remove()

@app.route('/', methods=['GET', 'POST'])
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
        comentarios = request.form['comentarios']
        foto = 'default.png'

        if not matricula or matricula == '':
            flash('Error: Se debe registrar una matricula.')
            return redirect(url_for('home'))
        
        egresado = db_session.query(models.Egresados)\
            .filter(models.Egresados.matricula==matricula)\
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
        
        if not comentarios:
            comentarios = ''

        if 'foto' in request.files and request.files['foto'].filename != '':
            foto_file = request.files['foto']

            if not validate_file_type(foto_file.filename, ALLOWED_IMAGE_TYPES):
                flash('Error: Tipo de archivo invalido.')
                return redirect(url_for('home'))
            
            foto  = guardar_foto(foto_file, FOTOS_EGRESADOS, True)
        
        nuevo_egresado = models.Egresados()

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

        db_session.add(nuevo_egresado)
        db_session.commit()

        flash(f'Info: Egresado {nuevo_egresado.nombre} registrado correctamente.')
        return redirect(url_for('home', include=nuevo_egresado.id, _anchor=f'popup/modal-egresado-{nuevo_egresado.id}'))

    egresados = db_session.query(models.Egresados)

    busqueda = request.args.get('buscar')
    
    if busqueda and busqueda != '':
        egresados = egresados.filter(or_(
            models.Egresados.nombre.like(f'%{busqueda}%'),
            models.Egresados.apellidos.like(f'%{busqueda}%'),
            models.Egresados.domicilio.like(f'%{busqueda}%'),
            models.Egresados.correo.like(f'%{busqueda}%'),
            models.Egresados.telefono.like(f'%{busqueda}%'),
            models.Egresados.curp.like(f'%{busqueda}%')
        ))
    
    generacion = request.args.get('generacion')

    if generacion and generacion != '' and generacion != 'all':
        egresados = egresados.filter(models.Egresados.generacion_id==generacion)

    modalidad = request.args.get('modalidad')

    if modalidad and modalidad != '' and modalidad != 'all':
        egresados = egresados.filter(models.Egresados.modalidad_id==modalidad)
    
    estatus = request.args.get('estatus')

    if estatus and estatus != '' and estatus != 'all':
        egresados = egresados.filter(models.Egresados.estatus==estatus)

    unidad = request.args.get('unidad')

    if unidad and unidad != '' and unidad != 'all':
        egresados = egresados.filter(models.Egresados.unidad_id==unidad)
    
    carrera = request.args.get('carrera')

    if carrera and carrera != '' and carrera != 'all':
        egresados = egresados.filter(models.Egresados.carrera_id==carrera)

    generaciones = db_session.query(models.Generaciones)

    if generaciones.count() == 0:
        flash("Info: Antes de poder registrar egresados, registra las generaciones de esta carrera en esta UES.")
        return redirect(url_for('generaciones'))

    if session_type == 'user':
        egresados = egresados.filter(
            and_(
                models.Egresados.unidad_id==session_user.unidad_id,
                models.Egresados.carrera_id==session_user.carrera_id
            )
        )

        generaciones = generaciones.filter(
            and_(
                models.Generaciones.unidad_id==session_user.unidad_id,
                models.Generaciones.carrera_id==session_user.carrera_id
            )
        )

    sort = request.args.get('sort')
    order = request.args.get('order')

    if sort and sort == 'nombre':
        if order and order == 'asc':
            egresados = egresados.order_by(models.Egresados.nombre.asc())
        else:
            egresados = egresados.order_by(models.Egresados.nombre.desc())
    
    elif sort and sort == 'apellidos':
        if order and order == 'asc':
            egresados = egresados.order_by(models.Egresados.apellidos.asc())
        else:
            egresados = egresados.order_by(models.Egresados.apellidos.desc())
    
    elif sort and sort == 'modalidad':
        if order and order == 'asc':
            egresados = egresados.join(models.Modalidades).order_by(models.Modalidades.nombre.asc())
        else:
            egresados = egresados.join(models.Modalidades).order_by(models.Modalidades.nombre.desc())
    
    elif sort and sort == 'estatus':
        if order and order == 'asc':
            egresados = egresados.order_by(models.Egresados.estatus.asc())
        else:
            egresados = egresados.order_by(models.Egresados.estatus.desc())
    
    elif sort and sort == 'generacion':
        if order and order == 'asc':
            egresados = egresados.join(models.Generaciones).order_by(models.Generaciones.anio_inicio.asc())
        
    else:
        egresados = egresados.join(models.Generaciones).order_by(models.Generaciones.anio_inicio.desc())
    
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
        include = db_session.query(models.Egresados).get(include)

        if include and not include in egresados:
            egresados.insert(0, include)

    generaciones = generaciones.all()
    modalidades = db_session.query(models.Modalidades).all()

    unidades = []
    carreras = []

    if session_type == 'admin':
        unidades = db_session.query(models.Unidades).all()
        carreras = db_session.query(models.Carreras).all()

    return render_template('home.html',
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

@app.post('/egresado/<id>/file')
def egresados_addfile(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresado = db_session.query(models.Egresados).get(id)

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
    
    ruta = guardar_archivo(fichero_file, FICHEROS_ADJUNTOS)

    nuevo_fichero = models.Ficheros()

    nuevo_fichero.ruta = ruta
    nuevo_fichero.nombre = secure_filename(fichero_file.filename)
    nuevo_fichero.egresado_id = egresado.id

    db_session.add(nuevo_fichero)
    db_session.commit()

    flash(f'Info: El fichero {nuevo_fichero.nombre} se adjunto correctamente a {egresado.nombre}')
    return redirect(url_for('home', include=egresado.id, _anchor=f'popup/modal-egresado-{egresado.id}'))

@app.get('/egresado/file/<id>/delete')
def egresado_delfile(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    fichero = db_session.query(models.Ficheros).get(id)

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

@app.get('/egresados/<id>/delete')
def egresados_delete(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresado = db_session.query(models.Egresados).get(id)

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

@app.post('/egresados/<id>/update')
def egresados_update(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresado = db_session.query(models.Egresados).get(id)

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

    if matricula and matricula != '':
        egresado_check = db_session.query(models.Egresados)\
            .filter(models.Egresados.matricula==matricula)\
            .first()
        
        if egresado_check:
            flash(f'Error: La matricula {matricula} ya esta registrada.')
            return redirect(url_for('home'))

        egresado.matricula = matricula
    
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
        
        egresado.foto  = guardar_foto(foto_file, FOTOS_EGRESADOS, True)
    
    db_session.add(egresado)
    db_session.commit()

    flash(f'Info: Egresado {egresado.nombre} actualizado correctamente.')
    return redirect(url_for('home', include=egresado.id, _anchor=f'popup/modal-egresado-{egresado.id}'))

@app.post('/generaciones/<id>/update')
def generaciones_update(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    generacion = db_session.query(models.Generaciones).get(id)

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
        
        generacion.foto  = guardar_foto(foto_file, FOTOS_GENERACIONALES)

    if anio_inicio and anio_inicio != '':
        generacion.anio_inicio = anio_inicio
    
    if anio_final and anio_final != '':
        generacion.anio_final = anio_final

    db_session.add(generacion)
    db_session.commit()

    flash('Info: Generacion actualizada correctamente.')
    return redirect(url_for('generaciones'))

@app.get('/generaciones/<id>/delete')
def generaciones_delete(id):
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    generacion = db_session.query(models.Generaciones).get(id)

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

@app.route('/generaciones', methods=['GET', 'POST'])
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
            
            foto = guardar_foto(foto_file, FOTOS_GENERACIONALES)

        if not anio_inicio or anio_inicio == '':
            flash('Error: No se proporciono el año de ingreso.')
            return redirect(url_for('generaciones'))
        
        if not anio_final or anio_final == '':
            flash('Error: No se proporciono el año de egreso.')
            return redirect(url_for('generaciones'))
        
        nueva_generacion = models.Generaciones()

        nueva_generacion.anio_inicio = anio_inicio
        nueva_generacion.anio_final = anio_final
        nueva_generacion.foto = foto
        nueva_generacion.unidad_id = session_user.unidad_id
        nueva_generacion.carrera_id = session_user.carrera_id

        db_session.add(nueva_generacion)
        db_session.commit()

    generaciones = db_session.query(models.Generaciones)

    if session_type == 'user':
        generaciones = generaciones.filter(
            and_(
                models.Generaciones.unidad_id==session_user.unidad_id,
                models.Generaciones.carrera_id==session_user.carrera_id
            )
        )

    generaciones = generaciones.all()

    return render_template('generaciones.html',
        generaciones=generaciones,
        session_type=session_type,
        session_user=session_user)

@app.get('/reportes')
def reportes():
    session_type = get_session_type()

    if not session_type:
        return redirect(url_for('login'))
    
    session_user = get_user_from_session()
    
    egresados = db_session.query(models.Egresados)
    generaciones = db_session.query(models.Generaciones)

    if session_type == 'user':
        egresados = egresados.filter(
            and_(
                models.Egresados.unidad_id==session_user.unidad_id,
                models.Egresados.carrera_id==session_user.carrera_id
            )
        )

        generaciones = generaciones.filter(
            and_(
                models.Generaciones.unidad_id==session_user.unidad_id,
                models.Generaciones.carrera_id==session_user.carrera_id
            )
        )
    
    generaciones = generaciones.all()

    return render_template('reportes.html',
        generaciones=generaciones,
        egresados=egresados,
        models=models,
        and_=and_,
        session_type=session_type,
        session_user=session_user,
        fecha_de_reporte=date.today())

@app.route('/admin/unidades', methods=['GET', 'POST'])
def admin_unidades():
    session_type = get_session_type()

    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))

    session_user = get_user_from_session()
    
    if request.method == 'POST':
        nombre = request.form['nombre']

        if not nombre or nombre == '':
            flash('Error: Debes indicar un nombre.')
            return redirect(url_for('admin_unidades'))
        
        nueva_unidad = models.Unidades()

        nueva_unidad.nombre = nombre

        db_session.add(nueva_unidad)
        db_session.commit()

    unidades = db_session.query(models.Unidades).all()
    
    return render_template('admin.html',
        active='unidades',
        unidades=unidades,
        session_type=session_type,
        session_user=session_user)

@app.get('/admin/unidades/<id>/delete')
def admin_unidades_delete(id):
    session_type = get_session_type()

    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    unidad = db_session.query(models.Unidades).get(id)

    if not unidad:
        flash('Error: Unidad no encontrada.')
        return redirect(url_for('admin_unidades'))
    
    db_session.delete(unidad)
    db_session.commit()

    flash('Info: Unidad eliminada correctamente.')
    return redirect(url_for('admin_unidades'))

@app.post('/admin/unidades/<id>/update')
def admin_unidades_update(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    unidad = db_session.query(models.Unidades).get(id)

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

@app.route('/admin/carreras', methods=['GET', 'POST'])
def admin_carreras():
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']

        if not nombre or nombre == '':
            flash('Error: Indica el nombre de la carrera.')
            return redirect(url_for('admin_carreras'))
        
        nueva_carrera = models.Carreras()

        nueva_carrera.nombre = nombre

        db_session.add(nueva_carrera)
        db_session.commit()
    
    carreras = db_session.query(models.Carreras).all()
    return render_template('admin.html',
        active='carreras',
        carreras=carreras,
        session_type=session_type)

@app.get('/admin/carreras/<id>/delete')
def admin_carreras_delete(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    carrera = db_session.query(models.Carreras).get(id)

    if not carrera:
        flash('Error: Carrera no encontrada.')
        return redirect(url_for('admin_carreras'))
    
    db_session.delete(carrera)
    db_session.commit()

    flash('Info: Carrera eliminada correctamente.')
    return redirect(url_for('admin_carreras'))

@app.post('/admin/carreras/<id>/update')
def admin_carreras_update(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    carrera = db_session.query(models.Carreras).get(id)

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

@app.get('/admin/modalidades/<id>/delete')
def modalidades_delete(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    modalidad = db_session.query(models.Modalidades).get(id)

    if not modalidad:
        flash('Error: Modalidad no encontrada.')
        return redirect(url_for('modalidades'))
    
    if modalidad.manual != 'default.pdf':
        os.remove(MANUALES_MODALIDADES + modalidad.manual)
    
    db_session.delete(modalidad)
    db_session.commit()

    flash('Info: Modalidad eliminada correctamente.')
    return redirect(url_for('modalidades'))

@app.post('/admin/modalidades/<id>/update')
def modalidades_update(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    modalidad = db_session.query(models.Modalidades).get(id)

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

        modalidad.manual = guardar_archivo(manual_file, MANUALES_MODALIDADES)
    
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

@app.route('/admin/modalidades', methods=['GET', 'POST'])
def modalidades():
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        manual = 'default.pdf'
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        if 'manual' in request.files and request.files['manual'].filename != '':
            manual_file = request.files['manual']

            if not validate_file_type(manual_file.filename, ALLOWED_DOC_TYPES):
                flash('Error: Tipo de archivo invalido.')
                return redirect(url_for('modalidades'))
            
            manual = guardar_archivo(manual_file, MANUALES_MODALIDADES)

        if not nombre or nombre == '':
            flash('Error: No se proporciono el nombre de la modalidad.')
            return redirect(url_for('modalidades'))
        
        if not descripcion or descripcion == '':
            flash('Error: No se proporciono la descripcion de la modalidad.')
            return redirect(url_for('modalidades'))
        
        nueva_modalidad = models.Modalidades()

        nueva_modalidad.manual = manual
        nueva_modalidad.nombre = nombre
        nueva_modalidad.descripcion = descripcion

        db_session.add(nueva_modalidad)
        db_session.commit()

    modalidades = db_session.query(models.Modalidades)

    return render_template('admin.html',
        active='modalidades',
        modalidades=modalidades,
        session_type=session_type)

@app.get('/admin/usuarios')
def admin_usuarios():
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    unidades = db_session.query(models.Unidades).all()
    carreras = db_session.query(models.Carreras).all()
    usuarios = db_session.query(models.Usuarios).all()

    return render_template('admin.html',
        active='usuarios',
        unidades=unidades,
        carreras=carreras,
        usuarios=usuarios,
        session_type=session_type)

@app.post('/usuario')
def usuario_post():
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    matricula = request.form['matricula']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido-paterno']
    apellido_materno = request.form['apellido-materno']
    unidad_id = request.form['unidad-id']
    carrera_id = request.form['carrera-id']

    if not matricula or matricula == '':
        flash('Error: Se debe indicar una matricula.')
        return redirect(url_for('admin_usuarios'))
    
    check_usuario = db_session.query(models.Usuarios).filter(models.Usuarios.matricula==matricula).first()

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
    
    nuevo_usuario = models.Usuarios()

    nuevo_usuario.matricula = matricula
    nuevo_usuario.nombre = nombre
    nuevo_usuario.apellido_paterno = apellido_paterno
    nuevo_usuario.apellido_materno = apellido_materno
    nuevo_usuario.clave = matricula
    nuevo_usuario.unidad_id = unidad_id
    nuevo_usuario.carrera_id = carrera_id

    db_session.add(nuevo_usuario)
    db_session.commit()

    flash('Info: Usuario creado correctamente.')
    return redirect(url_for('admin_usuarios'))

@app.get('/usuario/<id>/delete')
def usuario_delete(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    usuario = db_session.query(models.Usuarios).get(id);

    if not usuario:
        flash('Error: Usuario no encontrado.')
        return redirect(url_for('admin_usuarios'))
    
    db_session.delete(usuario)
    db_session.commit()

    flash('Info: Usuario eliminado correctamente.')
    return redirect(url_for('admin_usuarios'))

@app.get('/usuario/<id>/reset')
def usuario_reset(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    usuario = db_session.query(models.Usuarios).get(id);

    if not usuario:
        flash('Error: Usuario no encontrado.')
        return redirect(url_for('admin_usuarios'))
    
    usuario.clave = usuario.matricula
    
    db_session.add(usuario)
    db_session.commit()

    flash('Info: Usuario reseteado correctamente.')
    return redirect(url_for('admin_usuarios'))

@app.post('/usuario/<id>/update')
def usuario_update(id):
    session_type = get_session_type()
    
    if not session_type or session_type != 'admin':
        return redirect(url_for('login'))
    
    usuario = db_session.query(models.Usuarios).get(id);

    if not usuario:
        flash('Error: usuario no encontrado.')
        return redirect(url_for('admin_suaurios'))
    
    matricula = request.form['matricula']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido-paterno']
    apellido_materno = request.form['apellido-materno']
    unidad_id = request.form['unidad-id']
    carrera_id = request.form['carrera-id']

    if matricula and matricula != '':
        check_usuario = db_session.query(models.Usuarios).filter(models.Usuarios.matricula==matricula).first()

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
    
    db_session.add(usuario)
    db_session.commit()

    flash(f'Info: Usuario {usuario.nombre} actualizado correctamente')
    return redirect(url_for('admin_usuarios'))

@app.route('/login', methods=['GET', 'POST'])
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
            session['type'] = 'admin'
            return redirect(url_for('admin_unidades'))

        usuario = db_session.query(models.Usuarios).filter(
            and_(
                    models.Usuarios.matricula==matricula,
                    models.Usuarios.clave==clave
                )
        ).first()

        if not usuario:
            flash('Error: Credenciales invalidas.')
            return redirect(url_for('login'))
        
        session['type'] = 'user'
        session['user_id'] = usuario.id
        
        if usuario.clave == usuario.matricula:
            return redirect(url_for('change_password'))
        
        return redirect(url_for('home'))

    return render_template('login.html')

@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/change/password', methods=['GET', 'POST'])
def change_password():
    session_type = get_session_type()

    if session_type != 'user':
        return redirect(url_for('home'))
    
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

    return render_template('change-password.html', session_user=session_user)

@app.get('/info')
def info():
    session_type = get_session_type()    
    session_user = get_user_from_session()

    generaciones = db_session.query(models.Generaciones).all()
    modalidades = db_session.query(models.Modalidades).all()
    titulados = {}
    total_titulados = 0
    total_egresados = db_session.query(models.Egresados).count()
    total_carreras = db_session.query(models.Carreras).count()

    for modalidad in modalidades:
        titulados[modalidad.id] = db_session.query(models.Egresados).filter(
            and_(
                models.Egresados.modalidad_id==modalidad.id,
                models.Egresados.estatus==3
            )
        ).count()

        total_titulados += titulados[modalidad.id]

    return render_template('info.html', 
        session_type=session_type, 
        session_user=session_user,
        generaciones=generaciones,
        modalidades=modalidades,
        titulados=titulados,
        total_titulados=total_titulados,
        total_egresados=total_egresados,
        total_carreras=total_carreras)

@app.get('/blog')
def blog():
    session_type = get_session_type()    
    session_user = get_user_from_session()

    publicaciones = db_session.query(models.Publicaciones).all()

    return render_template('blog.html', 
                           session_type=session_type,
                           session_user=session_user,
                           publicaciones=publicaciones)

@app.post('/blog_post')
def blog_post():
    session_type = get_session_type()

    if not session_type or session_type != 'admin':
        flash('No tienes permiso para esto')
        return redirect(url_for('login'))

    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    contenido = request.form['contenido']

    if not 'portada' in request.files or request.files['portada'].filename == '':
        flash('Error: Debes seleccionar una foto de portada')
        return redirect(url_for('blog', _anchor='popup/publicar-blog-modal'))

    portada_file = request.files['portada']

    if not validate_file_type(portada_file.filename, ALLOWED_IMAGE_TYPES):
        flash('Error: Tipo de archivo invalido.')
        return redirect(url_for('blog', _anchor='popup/publicar-blog-modal'))
    
    portada  = guardar_foto(portada_file, FOTOS_BLOG, True)

    nueva_publicacion = models.Publicaciones()

    nueva_publicacion.titulo = titulo
    nueva_publicacion.descripcion = descripcion
    nueva_publicacion.contenido = contenido
    nueva_publicacion.portada = portada
    nueva_publicacion.fecha = date.today()

    db_session.add(nueva_publicacion)
    db_session.commit()

    flash('Info: Se publico la entrada correctamente')
    return redirect(url_for('blog'))

@app.get('/blog/<id>')
def blog_entry(id):
    session_type = get_session_type()    
    session_user = get_user_from_session()

    publicacion = db_session.query(models.Publicaciones).get(id)

    comments_data_href = request.base_url + f"#{publicacion.titulo.replace(' ', '-')}"

    return render_template('blog/entry.html', 
                           publicacion=publicacion,
                           session_type=session_type,
                           session_user=session_user,
                           comments_data_href=comments_data_href)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
