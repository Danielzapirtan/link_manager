from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Important for flash messages

# Database setup (using SQLite)
DATABASE = 'urls.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    return db

def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder TEXT DEFAULT 'root',
            title TEXT NOT NULL,
            url TEXT NOT NULL
        )
    ''')
    db.commit()
    db.close()

create_table()  # Create table if it doesn't exist


@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM urls ORDER BY folder, title")  # Default sorting
    urls = cursor.fetchall()
    db.close()
    return render_template('index.html', urls=urls)


@app.route('/add', methods=['GET', 'POST'])
def add_url():
    if request.method == 'POST':
        folder = request.form['folder'] or 'root'  # Default to 'root' folder
        title = request.form['title']
        url = request.form['url']

        if not title or not url:
            flash("Title and URL are required!")
            return redirect(url_for('add_url'))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO urls (folder, title, url) VALUES (?, ?, ?)", (folder, title, url))
            db.commit()
            flash("URL added successfully!")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:  # Handle duplicate entries (if needed)
            flash("A URL with that title already exists (in this folder).")
            return redirect(url_for('add_url'))
        finally:
            db.close()

    return render_template('add.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_url(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        folder = request.form['folder'] or 'root'
        title = request.form['title']
        url = request.form['url']

        if not title or not url:
            flash("Title and URL are required!")
            return redirect(url_for('edit_url', id=id))  # Stay on edit page

        try:
            cursor.execute("UPDATE urls SET folder=?, title=?, url=? WHERE id=?", (folder, title, url, id))
            db.commit()
            flash("URL updated successfully!")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash("A URL with that title already exists (in this folder).")
            return redirect(url_for('edit_url', id=id))  # Stay on edit page

        finally:
            db.close()

    cursor.execute("SELECT * FROM urls WHERE id=?", (id,))
    url_data = cursor.fetchone()
    db.close()

    if url_data:
        return render_template('edit.html', url_data=url_data)
    else:
        return "URL not found"  # Or redirect to an error page


@app.route('/delete/<int:id>')
def delete_url(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM urls WHERE id=?", (id,))
    db.commit()
    db.close()
    flash("URL deleted!")
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search_urls():
    query = request.args.get('q')
    if query:
        db = get_db()
        cursor = db.cursor()
        # Basic search (case-insensitive)
        cursor.execute("SELECT * FROM urls WHERE title LIKE ? OR url LIKE ? ORDER BY folder, title", ('%' + query + '%', '%' + query + '%'))
        results = cursor.fetchall()
        db.close()
        return render_template('index.html', urls=results, search_query=query) #Pass query to template
    return redirect(url_for('index')) #Redirect to index if no query


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5040)
