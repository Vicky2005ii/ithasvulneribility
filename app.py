from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Setup a temporary database in memory
def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute("CREATE TABLE users (username TEXT, password TEXT)")
    c.execute("INSERT INTO users VALUES ('admin', 'secret123')")
    c.execute("INSERT INTO users VALUES ('user', 'pass')")
    conn.commit()
    return conn

@app.route('/')
def home():
    return '''
    <h1>Vulnerable App Home</h1>
    <a href="/login">Go to Login (SQLi)</a><br>
    <a href="/search?q=test">Go to Search (XSS)</a>
    '''

# 1. THE VULNERABLE LOGIN (SQL Injection)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = init_db()
        c = conn.cursor()
        
        # VULNERABILITY: Directly formatting the string allows SQL injection!
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"Executing Query: {query}")
        
        c.execute(query)
        user = c.fetchone()
        
        if user:
            return f"Welcome, {user[0]}! You are logged in."
        else:
            return "Invalid credentials."
            
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="text" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# 2. THE VULNERABLE SEARCH (XSS)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULNERABILITY: render_template_string executes whatever HTML/JS is in 'query'
    return render_template_string(f"You searched for: {query}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
