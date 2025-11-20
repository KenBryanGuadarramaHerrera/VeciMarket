import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Añadimos el parámetro 'config_overrides'
def create_app(config_overrides=None):
    app = Flask(__name__)
    
    # Configuración por defecto (Base de datos)
    app.config['SECRET_KEY'] = 'clave-secreta-proyecto-unam'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    
    #  Si nos pasan una config de prueba, la usamos ANTES de conectar la BD
    if config_overrides:
        app.config.update(config_overrides)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import Usuario

    @login_manager.user_loader
    def load_user(id):
        return db.session.get(Usuario, int(id)) # Actualizado para evitar el warning Legacy

    # Registro de Blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .inventario import inventario as inventario_blueprint
    app.register_blueprint(inventario_blueprint, url_prefix='/inventario')
    
    from .market import market as market_blueprint
    app.register_blueprint(market_blueprint)
    
    from .delivery import delivery as delivery_blueprint
    app.register_blueprint(delivery_blueprint, url_prefix='/delivery')
    
    # Manejo de error 404
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('404.html'), 404
    
    with app.app_context():
        db.create_all()
        
    return app