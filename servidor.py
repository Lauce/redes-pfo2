from flask import Flask, request, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
DB = "tareas.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario  TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario  TEXT    NOT NULL,
                titulo   TEXT    NOT NULL,
                hecha    INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    if not data or "usuario" not in data or "contraseña" not in data:
        return jsonify({"error": "Se requieren 'usuario' y 'contraseña'"}), 400

    usuario  = data["usuario"].strip()
    password = data["contraseña"]

    if not usuario or not password:
        return jsonify({"error": "Usuario y contraseña no pueden estar vacíos"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
                (usuario, hashed)
            )
            conn.commit()
        return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "usuario" not in data or "contraseña" not in data:
        return jsonify({"error": "Se requieren 'usuario' y 'contraseña'"}), 400

    usuario  = data["usuario"].strip()
    password = data["contraseña"]

    with get_db() as conn:
        row = conn.execute(
            "SELECT password FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()

    if row and bcrypt.checkpw(password.encode(), row["password"].encode()):
        return jsonify({"mensaje": f"Bienvenido, {usuario}!"}), 200
    return jsonify({"error": "Credenciales inválidas"}), 401


@app.route("/tareas", methods=["GET"])
def tareas():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>TAREAS</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap');

            * { margin: 0; padding: 0; box-sizing: border-box; }

            body {
                background: #0a0a0a;
                color: #f0f0f0;
                font-family: 'IBM Plex Mono', monospace;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px 20px;
            }

            .contenedor {
                max-width: 520px;
                width: 100%;
                border: 1px solid #f0f0f0;
                padding: 48px;
            }

            .titulo {
                font-size: 3rem;
                font-weight: 700;
                letter-spacing: -2px;
                line-height: 1;
                margin-bottom: 32px;
                text-transform: uppercase;
            }

            .linea {
                border: none;
                border-top: 1px solid #f0f0f0;
                margin-bottom: 32px;
            }

            .subtitulo {
                font-size: 0.7rem;
                letter-spacing: 4px;
                text-transform: uppercase;
                color: #888;
                margin-bottom: 16px;
            }

            ul {
                list-style: none;
            }

            li {
                padding: 14px 0;
                border-bottom: 1px solid #222;
                font-size: 0.9rem;
            }

            li:last-child {
                border-bottom: none;
            }

            .metodo {
                color: #f0f0f0;
                font-weight: 700;
                margin-right: 12px;
            }

            .ruta {
                color: #888;
            }

            .desc {
                display: block;
                font-size: 0.75rem;
                color: #555;
                margin-top: 4px;
                padding-left: 0;
            }

            .estado {
                margin-top: 32px;
                font-size: 0.7rem;
                letter-spacing: 3px;
                color: #444;
                text-transform: uppercase;
            }

            .punto {
                display: inline-block;
                width: 6px;
                height: 6px;
                background: #f0f0f0;
                border-radius: 50%;
                margin-right: 8px;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <div class="contenedor">
            <div class="titulo">Tareas</div>
            <hr class="linea">
            <p class="subtitulo">Endpoints disponibles</p>
            <ul>
                <li>
                    <span class="metodo">POST</span><span class="ruta">/registro</span>
                    <span class="desc">Crear un usuario nuevo</span>
                </li>
                <li>
                    <span class="metodo">POST</span><span class="ruta">/login</span>
                    <span class="desc">Iniciar sesión</span>
                </li>
                <li>
                    <span class="metodo">GET</span><span class="ruta">/tareas</span>
                    <span class="desc">Esta página</span>
                </li>
            </ul>
            <p class="estado"><span class="punto"></span>Sistema operativo</p>
        </div>
    </body>
    </html>
    """
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada.")
    print("Servidor corriendo en http://127.0.0.1:5000")
    app.run(debug=True)