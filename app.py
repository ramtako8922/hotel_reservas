from flask import Flask, render_template, request, redirect
import sqlite3
from models import init_db

app = Flask(__name__)
init_db()

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
        cursor.execute('INSERT INTO reservas (nombre, email, fecha, habitacion) VALUES (?, ?, ?, ?)',
                       (nombre, email, fecha, habitacion))
        conn.commit()
        conn.close()
        return redirect('/confirmacion')
    return render_template('reserva.html')

@app.route('/confirmacion')
def confirmacion():
    return render_template('confirmacion.html')

if __name__ == '__main__':
    app.run(debug=True)
