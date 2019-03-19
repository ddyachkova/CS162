from flask import Flask, render_template, request, url_for, redirect, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,  login_user, logout_user, login_required, current_user 



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Darya/Documents/todo/todo.db'
db = SQLAlchemy(app)

app.secret_key = 'fightclub'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




class Todo(db.Model):
	__tablename__ = 'Todo'
	id = db.Column(db.Integer, primary_key = True)
	text = db.Column(db.String(200))
	status = db.Column(db.String(6))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))


class User(UserMixin, db.Model):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(200))
	password = db.Column(db.String(200))
	todo_id = db.relationship('Todo', backref='user', lazy='dynamic')

db.create_all()
db.session.commit()


@app.route('/')
@login_required
### Main page. Gather the submissions to the lists, categorise them and pass to one of the cards.
def index():
	g.user = current_user
	todos, doings, dones = [], [], []
	tasks = Todo.query.filter_by(user_id = g.user.id).all()
	for t in tasks:
		if t.status == 'Todo':
			todos.append(t)
		if t.status == 'Doing':
			doings.append(t)
		if t.status == 'Done':
			dones.append(t)


	return render_template('index.html', todos=todos, doings=doings, dones=dones)

@app.route('/add', methods=['POST', 'GET'])

### Add new elements to one of the three cards at a time

def add():
	g.user = current_user
	todo = Todo(text=request.form['todoitem'], status = request.form['status'])
	todo.user = g.user
	db.session.add(todo)
	db.session.commit()

	return redirect(url_for('index'))

@app.route('/update/<id>')
### Upgrate the status of the task.
### Delete the tasks that are done from the list.
def update(id):
	todo = Todo.query.filter_by(id=int(id)).first()
	if todo.status == 'Todo':
		todo.status = 'Doing'
	elif todo.status == 'Doing':
		todo.status = 'Done'
	else:
		db.session.delete(todo)
	db.session.commit()
	return redirect(url_for('index'))
	#return '<h1>{}</h1>'.format(id)

@app.route('/delete/<id>', methods=['GET', 'POST', 'DELETE'])
### Delete a task from any of the lists
def delete(id):
	todo = Todo.query.filter_by(id=int(id)).first()
	db.session.delete(todo)
	db.session.commit()
	return redirect (url_for('index'))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
### Create a login. If the user is not registered - signup.
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user is None:
            error = 'Bad Credentials. Try again.'
            return render_template('signup.html', error=error)
        login_user(user)
        return redirect(url_for('index'))
    elif request.method == 'GET':
       return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
### Add the user to the database. No requirements on the username nor the password. 
def signup():
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		print (new_user)
		db.session.add(new_user)
		db.session.commit()
		return redirect('login')
	elif request.method == 'GET':
		return render_template('signup.html')


@app.route('/logout')
### Lof the user out
def logout():
	logout_user()
	return redirect('/login')

#@app.route('/home')
#@login_required
#def home():
#	return 'Welcome!'.fomat(app.current_user.id)



if __name__ == '__main__':
	app.run(debug=True)