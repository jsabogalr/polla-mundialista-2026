from flask import Flask, render_template, request
from models import db, Usuario, Partido, Pronostico

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/usuarios")
def usuarios():

    usuarios = Usuario.query.all()

    salida = "<h1>Participantes</h1><hr>"

    for usuario in usuarios:
        salida += f"{usuario.nombre}<br>"

    return salida


@app.route("/partidos")
def partidos():

    partidos = Partido.query.all()

    salida = "<h1>Partidos</h1><hr>"

    for partido in partidos:
        salida += (
            f"{partido.equipo_local} vs "
            f"{partido.equipo_visitante}<br>"
        )

    return salida


@app.route("/predicciones/<slug>", methods=["GET", "POST"])
def predicciones(slug):

    usuario = Usuario.query.filter_by(slug=slug).first()

    if not usuario:
        return "Usuario no encontrado"

    partidos = Partido.query.all()

    if request.method == "POST":

        for partido in partidos:

            local = request.form.get(f"local_{partido.id}")
            visitante = request.form.get(f"visitante_{partido.id}")

            if local and visitante:

                pronostico = Pronostico.query.filter_by(
                    usuario_id=usuario.id,
                    partido_id=partido.id
                ).first()

                if pronostico:

                    pronostico.pronostico_local = int(local)
                    pronostico.pronostico_visitante = int(visitante)

                else:

                    nuevo = Pronostico(
                        usuario_id=usuario.id,
                        partido_id=partido.id,
                        pronostico_local=int(local),
                        pronostico_visitante=int(visitante)
                    )

                    db.session.add(nuevo)

        db.session.commit()

        return f"Pronosticos guardados para {usuario.nombre}"

    return render_template(
        "predicciones.html",
        usuario=usuario,
        partidos=partidos
    )


@app.route("/ver-pronosticos")
def ver_pronosticos():

    pronosticos = Pronostico.query.all()

    salida = "<h1>Pronosticos Guardados</h1><hr>"

    for p in pronosticos:

        salida += (
            f"{p.usuario.nombre} | "
            f"{p.partido.equipo_local} "
            f"{p.pronostico_local} - "
            f"{p.pronostico_visitante} "
            f"{p.partido.equipo_visitante}"
            "<br>"
        )

    return salida


@app.route("/cargar-partidos")
def cargar_partidos():

    if Partido.query.count() == 0:

        partidos = [

            Partido(
                fecha="2026-06-18",
                equipo_local="Mexico",
                equipo_visitante="Corea del Sur"
            ),

            Partido(
                fecha="2026-06-18",
                equipo_local="Suiza",
                equipo_visitante="Bosnia y Herzegovina"
            ),

            Partido(
                fecha="2026-06-18",
                equipo_local="Canada",
                equipo_visitante="Qatar"
            )

        ]

        db.session.add_all(partidos)
        db.session.commit()

    return "Partidos cargados"

@app.route("/clasificacion")
def clasificacion():

    tabla = []

    usuarios = Usuario.query.all()

    for usuario in usuarios:

        puntos = 0
        exactos = 0

        pronosticos = Pronostico.query.filter_by(
            usuario_id=usuario.id
        ).all()

        for p in pronosticos:

            partido = p.partido

            if (
                partido.goles_local is None
                or partido.goles_visitante is None
            ):
                continue

            # Marcador exacto
            if (
                p.pronostico_local == partido.goles_local
                and
                p.pronostico_visitante == partido.goles_visitante
            ):
                puntos += 5
                exactos += 1

            else:

                resultado_real = (
                    partido.goles_local -
                    partido.goles_visitante
                )

                resultado_pronostico = (
                    p.pronostico_local -
                    p.pronostico_visitante
                )

                if (
                    (resultado_real > 0 and resultado_pronostico > 0)
                    or
                    (resultado_real < 0 and resultado_pronostico < 0)
                    or
                    (resultado_real == 0 and resultado_pronostico == 0)
                ):
                    puntos += 3

                if p.pronostico_local == partido.goles_local:
                    puntos += 1

                if p.pronostico_visitante == partido.goles_visitante:
                    puntos += 1

        tabla.append({
            "nombre": usuario.nombre,
            "puntos": puntos,
            "exactos": exactos
        })

    tabla.sort(
        key=lambda x: x["puntos"],
        reverse=True
    )

    return render_template(
        "clasificacion.html",
        tabla=tabla
    )
        
@app.route("/cargar-resultados")
def cargar_resultados():

    partidos = Partido.query.all()

    if len(partidos) >= 3:

        partidos[0].goles_local = 2
        partidos[0].goles_visitante = 1

        partidos[1].goles_local = 1
        partidos[1].goles_visitante = 0

        partidos[2].goles_local = 2
        partidos[2].goles_visitante = 0

        db.session.commit()

    return "Resultados cargados"

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        if Usuario.query.count() == 0:

            usuarios = [

                Usuario(
                    usuario="alejo",
                    nombre="Alejo",
                    slug="alejo"
                ),

                Usuario(
                    usuario="brenda",
                    nombre="Brenda",
                    slug="brenda"
                ),

                Usuario(
                    usuario="yazmin",
                    nombre="Yazmin",
                    slug="yazmin"
                ),

                Usuario(
                    usuario="geyber",
                    nombre="Geyber",
                    slug="geyber"
                )

            ]

            db.session.add_all(usuarios)
            db.session.commit()

    app.run(debug=True)
    
@app.route("/limpiar")
def limpiar():

    Pronostico.query.delete()
    Partido.query.delete()

    db.session.commit()

    return "Base limpiada"