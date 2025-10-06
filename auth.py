from flask import Blueprint, render_template, request, redirect, flash, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        if not nombre or not email or not password:
            flash('Por favor complete todos los campos')
            return render_template('registro.html')

        password_hash = generate_password_hash(password)

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO usuarios (nombre, email, password_hash) VALUES (?, ?, ?)',
                           (nombre, email, password_hash))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            flash('El email ya está registrado')
            return render_template('registro.html')

        return render_template('registro_confirmacion.html', nombre=nombre)
    return render_template('registro.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Por favor complete todos los campos')
            return render_template('login.html')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre, password_hash FROM usuarios WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[2], password):
            session['user_id'] = row[0]
            session['user_name'] = row[1]
            flash('Has iniciado sesión correctamente')
            return redirect(url_for('index'))
        else:
            flash('Email o contraseña incorrectos')
            return render_template('login.html')

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada')
    return redirect(url_for('index'))
