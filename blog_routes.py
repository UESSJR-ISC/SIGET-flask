
from datetime import date

from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import flash

from server_config import *
from server_utils import *
from server import app


@app.get('/blog')
def blog():
    session_type = get_session_type()    
    session_user = get_user_from_session()

    publicaciones = db_session.query(models.Publicaciones).all()

    return render_template('blog.html', 
                           session_type=session_type,
                           session_user=session_user,
                           publicaciones=publicaciones)

@app.post('/blog/create')
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
    
    portada  = save_picture(portada_file, FOTOS_BLOG, True)

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

@app.get('/blog/entry/<id>')
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
