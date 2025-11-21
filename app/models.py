from . import db
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    
    # Teléfono para contacto directo (WhatsApp)
    telefono = db.Column(db.String(20), nullable=True) 
    
    direccion_tienda = db.Column(db.String(200), nullable=True)
    calificacion = db.Column(db.Float, default=5.0)
    
    productos = db.relationship('Producto', backref='propietario', lazy=True)
    
    # Relaciones de Pedidos
    compras = db.relationship('Pedido', foreign_keys='Pedido.cliente_id', backref='cliente', lazy=True)
    entregas = db.relationship('Pedido', foreign_keys='Pedido.repartidor_id', backref='repartidor', lazy=True)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(50), default='General')
    imagen = db.Column(db.String(100), default='default.jpg')
    
    # NUEVO: Define si es 'producto' o 'servicio'
    tipo = db.Column(db.String(20), default='producto') 
    
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    
    tienda_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    total = db.Column(db.Float, nullable=False)
    tipo_entrega = db.Column(db.String(20), default='envio') 
    metodo_pago = db.Column(db.String(20), default='efectivo')
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    repartidor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    items = db.relationship('PedidoItem', backref='pedido', lazy=True)

class PedidoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    producto = db.relationship('Producto')