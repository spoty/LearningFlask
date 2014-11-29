from flask import Flask, render_template, request, session, redirect, url_for, flash, g
import sqlite3
from functools import wraps

DATABASE = 'blog.db'
USER = 'admin'
PASSWORD = 'default'
SECRET_KEY = '\x8bs\x8f\xb1\x9a\xa0?\xa1T\x1d{\\x06\x0f7\x8eM\\x11c\xfd\xf6\x9e\xd9\\x89s'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
        return redirect(url_for('login'))
    return wrap


@app.route("/", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USER'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid credentials!'
        else:
            session['logged_in'] = True
            return redirect(url_for('main'))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))


@app.route("/main")
@login_required
def main():
    with connect_db() as g.db:
        cur = g.db.execute('select * from posts')
        posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
    return render_template("main.html", posts=posts)


@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    post = request.form['post']
    if not title or not post:
        flash('All fields are required. Please try again.')
        return redirect(url_for('main'))
    else:
        with connect_db() as g.db:
            g.db.execute('insert into posts (title, post) values (?,?)',
                        [request.form['title'], request.form['post']])
            g.db.commit()
            flash('New entry was successfully posted!')
            return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True)
