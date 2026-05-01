from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = 'uploads'

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            msg = "Registered successfully!"
        except:
            msg = "User already exists!"

        conn.close()
        return msg + " <a href='/login'>Login</a>"

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT username, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[1] == password:
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid credentials! <a href='/login'>Try again</a>"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
# ---------------- HOME (FILES + SEARCH) ----------------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    search = request.args.get('search')
    files = os.listdir(UPLOAD_FOLDER)
     # Search filter
    if search:
        files = [f for f in files if search.lower() in f.lower()]

    return render_template('index.html', files=files, user=session['user'])

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    files = os.listdir(UPLOAD_FOLDER)

    total_files = len(files)
    total_size = 0
    images = docs = others = 0

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file)

        if os.path.exists(path):
            total_size += os.path.getsize(path)

        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images += 1
        elif file.lower().endswith(('.pdf', '.docx', '.txt')):
            docs += 1
        else:
            others += 1

    total_size = round(total_size / 1024, 2)

    return render_template(
        'dashboard.html',
        user=session['user'],
        total_files=total_files,
        total_size=total_size,
        images=images,
        docs=docs,
        others=others
    )

# ---------------- UPLOAD ----------------
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    file = request.files['file']

    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        if not os.path.exists(path):
            file.save(path)

    return redirect('/')

# ---------------- DOWNLOAD ----------------
@app.route('/download/<filename>')
def download(filename):
    if 'user' not in session:
        return redirect('/login')

    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------------- DELETE ----------------
@app.route('/delete/<filename>')
def delete(filename):
    if 'user' not in session:
        return redirect('/login')

    path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(path):
        os.remove(path)

    return redirect('/')
# ---------------- SEARCH PAGE ----------------
@app.route('/search')
def search_page():
    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search')
    files = os.listdir(UPLOAD_FOLDER)

    if search:
        files = [f for f in files if search.lower() in f.lower()]

    return render_template('search.html', files=files, user=session['user'])

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)