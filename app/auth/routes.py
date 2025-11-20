from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Usuario, db
from . import auth

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            
            
                # En la función login(), actualiza la redirección así:
            if usuario.rol == 'tienda':
                return redirect(url_for('inventario.dashboard'))
            elif usuario.rol == 'repartidor':  # <--- NUEVO
                return redirect(url_for('delivery.dashboard'))

            # Si es cliente:
            return redirect(url_for('market.catalogo'))
            
        flash('Email o contraseña incorrectos.')
        
    return render_template('auth/login.html')

@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        rol = request.form.get('rol') 
        
        usuario_existente = Usuario.query.filter_by(email=email).first()
        
        if usuario_existente:
            flash('El correo ya está registrado.')
            return redirect(url_for('auth.registro'))
        
        
        nuevo_usuario = Usuario(
            email=email, 
            nombre=nombre, 
            password=generate_password_hash(password), # Flask usará el método más seguro por defecto
            rol=rol
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Cuenta creada exitosamente. Por favor inicia sesión.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/registro.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))