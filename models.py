import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            fecha TEXT NOT NULL,
            habitacion TEXT NOT NULL
        )
    """)
    # Tabla para usuarios registrados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)
    # Asegurarse de que la tabla reservas tenga la columna user_id para enlazar con usuarios
    cursor.execute("PRAGMA table_info(reservas)")
    existing = [row[1] for row in cursor.fetchall()]
    if 'user_id' not in existing:
        try:
            cursor.execute('ALTER TABLE reservas ADD COLUMN user_id INTEGER')
        except Exception:
            # Si algo falla aquí, no interrumpimos la inicialización; la app seguirá usando la tabla sin user_id
            pass
    conn.commit()
    conn.close()
