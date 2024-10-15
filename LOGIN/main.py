from flask import Flask, request, render_template, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.secret_key = "clave_secreta"
6
# Configuración de SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuario para inicio de sesión
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    
    # Relación para los usuarios creados por el usuario registrado
    created_users = db.relationship('User', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo para los usuarios gestionados por los usuarios registrados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

# Cargar usuario para LoginManager
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta principal
@app.route('/')
def index():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

# Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    user = Usuario.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html", error="Credenciales incorrectas")

# Registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template("register.html", error="Las contraseñas no coinciden")
        if Usuario.query.filter_by(email=email).first() or Usuario.query.filter_by(username=username).first():
            return render_template("register.html", error="Usuario o correo ya registrado")
        new_user = Usuario(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("register.html")

# Dashboard: muestra solo los usuarios creados por el usuario actual
@app.route("/dashboard")
@login_required
def dashboard():
    users = User.query.filter_by(creator_id=current_user.id).all()  # Muestra solo usuarios creados por el usuario actual
    return render_template("dashboard.html", username=current_user.username, users=users)

# Crear Usuario: crea un nuevo usuario asociado al usuario actual
@app.route("/create_user", methods=["POST"])
@login_required
def create_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        flash("Usuario o correo ya registrado", "error")
    else:
        new_user = User(email=email, username=username, creator_id=current_user.id)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuario creado exitosamente", "success")
    return redirect(url_for('dashboard'))

# Editar Usuario
@app.route("/edit_user/<int:user_id>", methods=["POST"])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.username = request.form['username']
    user.email = request.form['email']
    db.session.commit()
    flash("Usuario actualizado exitosamente", "success")
    return redirect(url_for('dashboard'))

# Eliminar Usuario
@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado exitosamente", "success")
    return redirect(url_for('dashboard'))

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
