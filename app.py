from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
from models import init_db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
# Secret key para sesiones y flash. Cambiar en producción mediante la variable de entorno SECRET_KEY
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me')

init_db()

# Registrar blueprint de autenticación (definido en auth.py)
try:
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
except Exception:
    # Si auth.py no está presente aún, seguir sin fallo para permitir edición incremental
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserva', methods=['GET', 'POST'])
def reserva():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        fecha = request.form['fecha']
        habitacion = request.form['habitacion']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        user_id = session.get('user_id')
        if user_id:
            cursor.execute('INSERT INTO reservas (nombre, email, fecha, habitacion, user_id) VALUES (?, ?, ?, ?, ?)',
                           (nombre, email, fecha, habitacion, user_id))
        else:
            cursor.execute('INSERT INTO reservas (nombre, email, fecha, habitacion) VALUES (?, ?, ?, ?)',
                           (nombre, email, fecha, habitacion))
        conn.commit()
        conn.close()
        return redirect('/confirmacion')
    return render_template('reserva.html')

@app.route('/confirmacion')
def confirmacion():
    return render_template('confirmacion.html')


# Las rutas de registro/login/logout están definidas en el blueprint `auth` (archivo auth.py)


from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/mis_reservas')
@login_required
def mis_reservas():
    user_id = session.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, email, fecha, habitacion FROM reservas WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return render_template('mis_reservas.html', reservas=rows)


@app.route('/reservas/<int:res_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_reserva(res_id):
    user_id = session.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, email, fecha, habitacion, user_id FROM reservas WHERE id = ?', (res_id,))
    row = cursor.fetchone()
    if not row or row[5] != user_id:
        conn.close()
        flash('Reserva no encontrada o sin permiso')
        return redirect(url_for('mis_reservas'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        fecha = request.form.get('fecha')
        habitacion = request.form.get('habitacion')
        cursor.execute('UPDATE reservas SET nombre = ?, email = ?, fecha = ?, habitacion = ? WHERE id = ?',
                       (nombre, email, fecha, habitacion, res_id))
        conn.commit()
        conn.close()
        flash('Reserva actualizada')
        return redirect(url_for('mis_reservas'))

    conn.close()
    return render_template('editar_reserva.html', reserva=row)


@app.route('/reservas/<int:res_id>/eliminar', methods=['POST'])
@login_required
def eliminar_reserva(res_id):
    user_id = session.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM reservas WHERE id = ?', (res_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        conn.close()
        flash('Reserva no encontrada o sin permiso')
        return redirect(url_for('mis_reservas'))
    cursor.execute('DELETE FROM reservas WHERE id = ?', (res_id,))
    conn.commit()
    conn.close()
    flash('Reserva eliminada')
    return redirect(url_for('mis_reservas'))

if __name__ == '__main__':
    app.run(debug=True)
