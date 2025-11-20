from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Pedido, db
from . import delivery

@delivery.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol != 'repartidor':
        flash('Zona exclusiva para repartidores.')
        return redirect(url_for('market.index'))

    # Solo mostrar pedidos pendientes que requieran envío
    pedidos_disponibles = Pedido.query.filter_by(estado='pendiente', tipo_entrega='envio').all()
    
    mis_entregas = Pedido.query.filter_by(estado='en_camino', repartidor_id=current_user.id).all()

    return render_template('delivery/dashboard.html', 
                           disponibles=pedidos_disponibles, 
                           mis_entregas=mis_entregas)

@delivery.route('/aceptar/<int:id>')
@login_required
def aceptar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    
    if pedido.estado != 'pendiente':
        flash('No disponible.')
        return redirect(url_for('delivery.dashboard'))
    
    pedido.repartidor_id = current_user.id
    pedido.estado = 'en_camino'
    db.session.commit()
    
    flash('¡Pedido aceptado!')
    return redirect(url_for('delivery.dashboard'))

@delivery.route('/finalizar/<int:id>')
@login_required
def finalizar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    
    if pedido.repartidor_id != current_user.id:
        return "Acceso denegado", 403
        
    pedido.estado = 'entregado'
    db.session.commit()
    
    flash('Entrega completada.')
    return redirect(url_for('delivery.dashboard'))