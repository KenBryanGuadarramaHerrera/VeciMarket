from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from ..models import Producto, Pedido, PedidoItem, db
from . import market
from flask import jsonify

# ---  RUTA HOME (LANDING PAGE) ---
@market.route('/')
def home():
    return render_template('landing.html')

# --- RUTA DEL CATÁLOGO  ---
@market.route('/catalogo')
def catalogo():
    # Lógica de filtros 
    categoria = request.args.get('categoria')
    busqueda = request.args.get('q')
    
    query = Producto.query.filter(Producto.stock_actual > 0)
    
    if categoria:
        query = query.filter_by(categoria=categoria)
    if busqueda:
        query = query.filter(Producto.nombre.contains(busqueda))
        
    productos = query.all()
    categorias_raw = db.session.query(Producto.categoria).distinct().all()
    categorias = [c[0] for c in categorias_raw]
    
    return render_template('market/index.html', productos=productos, categorias=categorias)



@market.route('/agregar/<int:id>')
@login_required
def agregar_carrito(id):
    if current_user.rol == 'tienda':
        flash('Las tiendas no compran.')
        return redirect(url_for('market.catalogo')) 

    if 'carrito' not in session:
        session['carrito'] = []

    session['carrito'].append(id)
    session.modified = True
    flash('Producto agregado.')
    return redirect(url_for('market.catalogo')) 

@market.route('/eliminar_item/<int:id>')
@login_required
def eliminar_item_carrito(id):
    if 'carrito' in session:
        carrito = session['carrito']
        if id in carrito:
            carrito.remove(id)
            session['carrito'] = carrito
            session.modified = True
            flash('Producto eliminado del carrito.')
    return redirect(url_for('market.ver_carrito'))

@market.route('/carrito', methods=['GET', 'POST'])
@login_required
def ver_carrito():
    carrito_ids = session.get('carrito', [])
    productos_en_carrito = []
    total = 0
    
    for pid in carrito_ids:
        prod = Producto.query.get(pid)
        if prod:
            productos_en_carrito.append(prod)
            total += prod.precio

    if request.method == 'POST':
        if not productos_en_carrito:
            return redirect(url_for('market.catalogo')) 

        nuevo_pedido = Pedido(
            total=total,
            cliente_id=current_user.id,
            estado='pendiente',
            tipo_entrega=request.form.get('tipo_entrega'),
            metodo_pago=request.form.get('metodo_pago')
        )
        db.session.add(nuevo_pedido)
        db.session.commit() 
        
        for prod in productos_en_carrito:
            item = PedidoItem(pedido_id=nuevo_pedido.id, producto_id=prod.id)
            db.session.add(item)
            prod.stock_actual -= 1
            
        db.session.commit()
        session.pop('carrito', None)
        
        flash('¡Pedido realizado con éxito!')
        return redirect(url_for('market.historial'))

    return render_template('market/carrito.html', productos=productos_en_carrito, total=total)

@market.route('/mis_pedidos')
@login_required
def historial():
    pedidos = Pedido.query.filter_by(cliente_id=current_user.id).order_by(Pedido.fecha.desc()).all()
    return render_template('market/historial.html', pedidos=pedidos)

@market.route('/limpiar')
def limpiar_carrito():
    session.pop('carrito', None)
    return redirect(url_for('market.catalogo'))

@market.route('/api/productos')
def api_productos():
    productos = Producto.query.filter(Producto.stock_actual > 0).all()
    data = []
    for p in productos:
        data.append({
            'id': p.id,
            'nombre': p.nombre,
            'precio': p.precio,
            'tienda': p.propietario.nombre,
            'categoria': p.categoria,
            'imagen_url': url_for('static', filename='uploads/' + p.imagen, _external=True)
        })
    return jsonify({'status': 'ok', 'count': len(data), 'data': data})