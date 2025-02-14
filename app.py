from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def init_db():
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Home route - Display all links
@app.route('/')
def index():
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('SELECT * FROM links')
    links = c.fetchall()
    conn.close()
    return render_template('index.html', links=links)

# Add a new link
@app.route('/add', methods=['GET', 'POST'])
def add_link():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']

        conn = sqlite3.connect('links.db')
        c = conn.cursor()
        c.execute('INSERT INTO links (title, url) VALUES (?, ?)', (title, url))
        conn.commit()
        conn.close()

        flash('Link added successfully!')
        return redirect(url_for('index'))

    return render_template('add_link.html')

# Delete a link
@app.route('/delete/<int:id>')
def delete_link(id):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('DELETE FROM links WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Link deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)