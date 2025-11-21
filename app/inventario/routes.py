import os
import secrets
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models import Producto, Pedido, PedidoItem, db
from . import inventario


def solo_tiendas(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.rol != 'tienda':
            flash('Acceso denegado.')
            return redirect(url_for('market.home'))
        return func(*args, **kwargs)
    return wrapper

def guardar_imagen(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@inventario.route('/dashboard')
@login_required
@solo_tiendas
def dashboard():
    mis_productos = Producto.query.filter_by(tienda_id=current_user.id).all()
    
    # Alerta solo cuenta PRODUCTOS, no servicios
    alertas = sum(1 for p in mis_productos if p.tipo == 'producto' and p.stock_actual <= p.stock_minimo)
    
    nombres_prod = [p.nombre for p in mis_productos]
    stocks_prod = [p.stock_actual for p in mis_productos]

    return render_template('inventario/dashboard.html', 
                           productos=mis_productos, 
                           alertas=alertas,
                           nombres=nombres_prod,
                           datos=stocks_prod)


@inventario.route('/ventas')
@login_required
@solo_tiendas
def historial_ventas():
    ventas = PedidoItem.query.join(Producto).join(Pedido).filter(Producto.tienda_id == current_user.id).all()
    ingreso_total = sum(item.producto.precio * item.cantidad for item in ventas)
    return render_template('inventario/ventas.html', ventas=ventas, total=ingreso_total)

@inventario.route('/agregar', methods=['GET', 'POST'])
@login_required
@solo_tiendas
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo') 
        precio = float(request.form.get('precio'))
        descripcion = request.form.get('descripcion')
        categoria = request.form.get('categoria')
        stock = int(request.form.get('stock'))
        
        imagen_file = request.files.get('imagen')
        imagen_nombre = 'default.jpg'
        if imagen_file:
            imagen_nombre = guardar_imagen(imagen_file)

        nuevo_item = Producto(
            nombre=nombre, tipo=tipo, precio=precio, descripcion=descripcion,
            categoria=categoria, stock_actual=stock,
            imagen=imagen_nombre, tienda_id=current_user.id
        )
        
        db.session.add(nuevo_item)
        db.session.commit()
        return redirect(url_for('inventario.dashboard'))
        
    return render_template('inventario/agregar.html')

@inventario.route('/ajustar_stock/<int:id>', methods=['POST'])
@login_required
@solo_tiendas
def ajustar_stock(id):
    producto = Producto.query.get_or_404(id)
    if producto.propietario != current_user:
        return "Acceso denegado", 403
    
    # Solo se ajusta stock si es producto
    if producto.tipo == 'producto':
        producto.stock_actual = int(request.form.get('nuevo_stock'))
        db.session.commit()
        
    return redirect(url_for('inventario.dashboard'))