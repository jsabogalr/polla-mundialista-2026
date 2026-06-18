import pandas as pd

from app import app
from models import db, Usuario, Partido, Pronostico

ARCHIVO = "Polla mundialista.xlsx"

with app.app_context():

    print("Leyendo Excel...")

    df = pd.read_excel(
        ARCHIVO,
        header=1
    )

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    print("\nColumnas encontradas:")
    print(df.columns.tolist())

    # Limpiar datos anteriores
    Pronostico.query.delete()
    Partido.query.delete()

    db.session.commit()

    # Usuarios
    usuarios = {
        "BRENDA": "brenda",
        "YAZMIN": "yazmin",
        "GEYBER": "geyber",
        "ALEJO": "alejo"
    }

    usuarios_db = {}

    for nombre, slug in usuarios.items():

        usuario = Usuario.query.filter_by(
            slug=slug
        ).first()

        if not usuario:

            usuario = Usuario(
                usuario=slug,
                nombre=nombre.title(),
                slug=slug
            )

            db.session.add(usuario)
            db.session.flush()

        usuarios_db[nombre] = usuario

    db.session.commit()

    partidos_importados = 0
    pronosticos_importados = 0

    for _, fila in df.iterrows():

        try:

            if pd.isna(fila["PARTIDO"]):
                continue

            partido_texto = str(fila["PARTIDO"]).strip()

            if "x" not in partido_texto.lower():
                continue

            partes = partido_texto.split("x")

            if len(partes) != 2:
                continue

            equipo_local = partes[0].strip()
            equipo_visitante = partes[1].strip()

            partido = Partido(
                fecha=str(fila["FECHA"]),
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante
            )

            resultado = str(fila["RESULTADO"]).strip()

            if "_" in resultado:

                try:

                    goles_local, goles_visitante = resultado.split("_")

                    partido.goles_local = int(goles_local)
                    partido.goles_visitante = int(goles_visitante)
                    partido.estado = "finalizado"

                except:
                    pass

            db.session.add(partido)
            db.session.flush()

            partidos_importados += 1

            # Pronósticos
            for columna in ["BRENDA", "YAZMIN", "GEYBER", "ALEJO"]:

                valor = str(fila[columna]).strip()

                if (
                    valor.lower() == "x"
                    or valor.lower() == "nan"
                    or "_" not in valor
                ):
                    continue

                try:

                    local, visitante = valor.split("_")

                    pronostico = Pronostico(
                        usuario_id=usuarios_db[columna].id,
                        partido_id=partido.id,
                        pronostico_local=int(local),
                        pronostico_visitante=int(visitante)
                    )

                    db.session.add(pronostico)

                    pronosticos_importados += 1

                except:
                    continue

        except Exception as e:

            print(
                f"Error fila {_}: {e}"
            )

            continue

    db.session.commit()

print("\n===================================")
print("IMPORTACION FINALIZADA")
print("===================================")
print(f"Partidos: {partidos_importados}")
print(f"Pronosticos: {pronosticos_importados}")
print("===================================")