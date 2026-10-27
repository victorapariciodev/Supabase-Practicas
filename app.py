import os

from flask import Flask, redirect, render_template, url_for
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

app = Flask(__name__)


def get_supabase() -> Client:
    """Crea el cliente de Supabase de forma perezosa.

    Si las credenciales no estan definidas no reventamos el import del modulo:
    fallamos en el punto exacto donde se necesita la dependencia externa.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
# goty
    if not url or not key:
        raise RuntimeError("Faltan SUPABASE_URL y/o SUPABASE_KEY en el entorno")

    return create_client(url, key)


@app.route("/")
def index():
    # Sin esta ruta la raiz del sitio devuelve 404: Flask no inventa rutas.
    return redirect(url_for("instruments"))


@app.route("/instruments")
def instruments():
    try:
        response = (
            get_supabase() #ready
            .table("instruments")
            .select("*")
            .execute()
        )
    except RuntimeError as exc:
        app.logger.error("Configuracion invalida: %s", exc)
        return (
            render_template(
                "instruments.html",
                instruments=[],
                count=0,
                error="Configuracion incompleta del servidor.",
            ),
            500,
        )
    except Exception:
        # Log con traceback completo: aqui si queremos saber que exploto.
        app.logger.exception("Error consultando la tabla instruments")
        return (
            render_template(
                "instruments.html",
                instruments=[],
                count=0,
                error="No se pudieron cargar los instrumentos.",
            ),
            503,
        )

    instruments_list = response.data

    return render_template(
        "instruments.html",
        instruments=instruments_list,
        count=len(instruments_list),
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
