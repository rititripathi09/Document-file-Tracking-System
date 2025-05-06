from flask import Flask, session, flash, redirect, request, render_template, g, url_for, send_from_directory
from uuid import uuid4
import sqlite3, os

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='ab235f8410cb598895eedd6a0557d324a497e778419a3701fc552c464ed1f161',
    MAX_CONTENT_LENGTH=16*1024*1024,
    UPLOAD_FOLDER='documents'
)

@app.context_processor
def app_globals():
    return dict(style='style.css', script='script.js')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def teardown_db(e):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        handle = request.files['files']
        file = os.path.join(app.config['UPLOAD_FOLDER'], handle.filename)
        if handle:
            handle.save(file)
            db=get_db()
            db.execute('INSERT INTO files (name, phone, email, notes, file) VALUES(?,?,?,?,?)',(request.form['name'],request.form['phone'],request.form['email'],request.form['notes'],handle.filename))
            db.commit()
        return render_template('uploaded.html', file=f'/file/{handle.filename}')
    else:
        message = f'No Errors'
        return render_template('index.html', message=message)

@app.route("/file/<string:file>")
def download(file):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), file)

@app.route("/department", methods=['GET', 'POST'])
def catalog():
    return f'<p>Create Department</p>'

@app.route("/department/<uuid:type>", methods=['GET', 'POST'])
def list(type):
    return f'<p>Departmental Documents: {type}</p>'

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    db = get_db()
    departments=db.execute('SELECT * FROM departments').fetchall()
    files = db.execute('SELECT f.id,f.name,f.phone,f.email,f.notes,f.file,d.name as department FROM files f LEFT JOIN departments d ON (f.department=d.id)').fetchall()
    return render_template('dashboard.html', files=files, departments=departments)

@app.route("/dashboard/<int:file>", methods=['GET', 'POST'])
def update(file):
    if request.method=='POST':
        db=get_db()
        db.execute('UPDATE files SET department=? WHERE id=?',(request.form['department'], file))
        db.commit()
        return redirect(url_for("dashboard"))
    else:
        db=get_db()
        logs=db.execute('SELECT l.id, f.name as file, l.type as column, o.name as old, n.name as new,l.time,f.file as attachment FROM logs l LEFT JOIN files f ON (l.file=f.id) LEFT JOIN departments o ON(l.previous=o.id) LEFT JOIN departments n ON(l.updated=n.id) WHERE l.file=?', (file,)).fetchall()
        return render_template('log.html', logs=logs)

@app.route("/db")
def init():
    handle = get_db()
    #cursor = handle.cursor()
    with open('db.sql') as sql:
        handle.executescript(sql.read())
    return f'<p>Database Initialized</p>'