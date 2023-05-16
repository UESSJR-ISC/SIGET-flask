from sqlalchemy import Date
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import relationship, deferred


from database import Database


class Modalidades(Database):
    __tablename__ = "modalidades"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    descripcion = Column(String(150))
    manual = Column(String(54))


class Generaciones(Database):
    __tablename__ = "generaciones"

    id = Column(Integer, primary_key=True)
    anio_inicio = Column(Integer)
    anio_final = Column(Integer)
    foto = Column(String(54))

    unidad_id = Column(Integer, ForeignKey('unidades.id'))
    unidad = relationship("Unidades")

    carrera_id = Column(Integer, ForeignKey('carreras.id'))
    carrera = relationship("Carreras")


class Egresados(Database):
    __tablename__ = "egresados"

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

    modalidad_id = Column(Integer, ForeignKey('modalidades.id'))
    modalidad = relationship("Modalidades")

    generacion_id = Column(Integer, ForeignKey('generaciones.id'))
    generacion = relationship("Generaciones")

    unidad_id = Column(Integer, ForeignKey('unidades.id'))
    unidad = relationship("Unidades")

    carrera_id = Column(Integer, ForeignKey('carreras.id'))
    carrera = relationship("Carreras")

    ficheros = relationship("Ficheros", back_populates='egresado')


class Ficheros(Database):
    __tablename__ = "ficheros"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(54))
    ruta = Column(String(54))

    egresado_id = Column(Integer, ForeignKey('egresados.id'))
    egresado = relationship("Egresados", back_populates='ficheros')


class Unidades(Database):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(54))


class Carreras(Database):
    __tablename__ = "carreras"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(54))


class Usuarios(Database):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    matricula = Column(String(11))
    nombre = Column(String(32))
    apellido_paterno = Column(String(32))
    apellido_materno = Column(String(32))
    clave = Column(String(64))

    unidad_id = Column(Integer, ForeignKey('unidades.id'))
    unidad = relationship("Unidades")

    carrera_id = Column(Integer, ForeignKey('carreras.id'))
    carrera = relationship("Carreras")