from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True)


class Partido(db.Model):
    __tablename__ = "partidos"

    id = db.Column(db.Integer, primary_key=True)

    fecha = db.Column(db.String(20))
    equipo_local = db.Column(db.String(100), nullable=False)
    equipo_visitante = db.Column(db.String(100), nullable=False)

    goles_local = db.Column(db.Integer, nullable=True)
    goles_visitante = db.Column(db.Integer, nullable=True)

    estado = db.Column(db.String(20), default="pendiente")


class Pronostico(db.Model):
    __tablename__ = "pronosticos"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    partido_id = db.Column(
        db.Integer,
        db.ForeignKey("partidos.id"),
        nullable=False
    )

    pronostico_local = db.Column(db.Integer)
    pronostico_visitante = db.Column(db.Integer)

    usuario = db.relationship("Usuario")
    partido = db.relationship("Partido")