from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy

from  werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'somesecretkeythatonlyishouldknow'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    list_to_do = db.relationship('Todo', backref='user', lazy=True)

@app.route('/accueil')
def accueil():
    if not g.user:
        return render_template('accueil.html',log_out=False)
    return render_template('accueil.html',log_out=True)
@app.route('/contactus')
def cus():
    if not g.user:
        return render_template('contactus.html',log_out=False)
    return render_template('contactus.html',log_out=True)

@app.route("/")
def home():
    if not g.user:
        return redirect(url_for('login'))
    todo_list = User.query.get(g.user.id).list_to_do
    log_out = True
    return render_template("base.html", todo_list=todo_list,log_out=log_out)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False,user_id = g.user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not g.user:
        if request.method == 'POST':
            session.pop('user_id', None)
            name = request.form['name']
            eml = request.form['email']
            pwd = request.form['password']

            user = User(name=name,email=eml,password=generate_password_hash(pwd))
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('accueil'))

        return render_template('sign-up.html')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not g.user:
        if request.method == 'POST':
            session.pop('user_id', None)

            eml = request.form['email']
            pwd = request.form['password']

            user = User.query.filter_by(email = eml).first()
            if user and check_password_hash(user.password,pwd)  :
                session['user_id'] = user.id
                return redirect(url_for('accueil'))

            return render_template('login.html',wrong= True)

        return render_template('login.html')
    return redirect(url_for('home'))

@app.route('/sign_out')
def sign_out():
    session.pop('user_id')
    log_out = False
    return redirect(url_for('login',log_out=log_out))
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
