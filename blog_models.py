from sqlalchemy import Date
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer


from database import Database


class Publicaciones(Database):
    __tablename__ = "blog_publicaciones"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(90))
    descripcion = Column(String(120))
    contenido = Column(String(4096))
    portada = Column(String(54))
    fecha = Column(Date)