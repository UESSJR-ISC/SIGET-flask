from sqlalchemy import Date
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


from database import Database


class Modalidades(Database):
    __tablename__ = "siget_modalidades"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    descripcion = Column(String(150))
    manual = Column(String(54))


class Generaciones(Database):
    __tablename__ = "siget_generaciones"

    id = Column(Integer, primary_key=True)
    anio_inicio = Column(Integer)
    anio_final = Column(Integer)
    foto = Column(String(54))

    unidad_id = Column(Integer, ForeignKey('siget_unidades.id'))
    unidad = relationship("Unidades")

    carrera_id = Column(Integer, ForeignKey('siget_carreras.id'))
    carrera = relationship("Carreras")


class Egresados(Database):
    __tablename__ = "siget_egresados"

    id = Column(Integer, primary_key=True)
    matricula = Column(String(10))
    nombre = Column(String(50))
    apellidos = Column(String(150))
    domicilio = Column(String(150))
    curp = Column(String(20))
    telefono = Column(String(10))
    correo = Column(String(50))
    sexo = Column(String(1))
    estatus = Column(Integer)
    comentarios = Column(String(250))
    foto = Column(String(54))

    modalidad_id = Column(Integer, ForeignKey('siget_modalidades.id'))
    modalidad = relationship("Modalidades")

    generacion_id = Column(Integer, ForeignKey('siget_generaciones.id'))
    generacion = relationship("Generaciones")

    unidad_id = Column(Integer, ForeignKey('siget_unidades.id'))
    unidad = relationship("Unidades")

    carrera_id = Column(Integer, ForeignKey('siget_carreras.id'))
    carrera = relationship("Carreras")

    ficheros = relationship("Ficheros", back_populates='egresado')

    titulacion_fecha = Column(String(10))
    proyecto_escrito_titulo = Column(String(250))

    titulacion_presidente_nombre = Column(String(200))
    titulacion_presidente_cedula = Column(String(10))

    titulacion_secretario_nombre = Column(String(200))
    titulacion_secretario_cedula = Column(String(10))

    titulacion_vocal_nombre = Column(String(200))
    titulacion_vocal_cedula = Column(String(10))

    titulacion_suplente_nombre = Column(String(200))
    titulacion_suplente_cedula = Column(String(10))

    comite_presidente_nombre = Column(String(200))
    comite_presidente_cedula = Column(String(10))

    comite_secretario_nombre = Column(String(200))
    comite_secretario_cedula = Column(String(10))

    comite_vocal_nombre = Column(String(200))
    comite_vocal_cedula = Column(String(10))


class Ficheros(Database):
    __tablename__ = "siget_ficheros"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(54))
    ruta = Column(String(54))

    egresado_id = Column(Integer, ForeignKey('siget_egresados.id'))
    egresado = relationship("Egresados", back_populates='ficheros')


class Unidades(Database):
    __tablename__ = "siget_unidades"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(54))


class Carreras(Database):
    __tablename__ = "siget_carreras"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(54))


class Usuarios(Database):
    __tablename__ = "siget_usuarios"

    id = Column(Integer, primary_key=True)
    matricula = Column(String(11))
    nombre = Column(String(32))
    apellido_paterno = Column(String(32))
    apellido_materno = Column(String(32))
    clave = Column(String(64))

    unidad_id = Column(Integer, ForeignKey('siget_unidades.id'))
    unidad = relationship("Unidades")

    carrera_id = Column(Integer, ForeignKey('siget_carreras.id'))
    carrera = relationship("Carreras")

    rol = Column(Integer)