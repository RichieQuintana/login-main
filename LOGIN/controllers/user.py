from flask import Blueprint, render_template, request, redirect, url_for
from main import db
from models.user import Usuario

user_bp = Blueprint('user_bp', __name__)

# Ruta para ver los usuarios
@user_bp.route('/manage_users')
def manage_users():
    users = Usuario.query.all()
    return render_template('dashboard.html', users=users)

# Ruta para crear un usuario
@user_bp.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_user = Usuario(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_bp.manage_users'))
    
    return render_template('create_user.html')

# Ruta para editar un usuario
@user_bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']

        if request.form['password']:
            user.set_password(request.form['password'])
        
        db.session.commit()
        return redirect(url_for('user_bp.manage_users'))

    return render_template('edit_user.html', user=user)

# Ruta para eliminar un usuario
@user_bp.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user_bp.manage_users'))
