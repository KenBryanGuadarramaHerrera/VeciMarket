import unittest
from app import create_app, db
from app.models import Usuario, Producto, Pedido
from werkzeug.security import generate_password_hash

class VeciMarketTestCase(unittest.TestCase):
    
    def setUp(self):
        # Usamos memoria RAM:
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True,
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # --- PRUEBA 1: REGISTRO Y DATOS ---
    def test_registro_usuario(self):
        print("\n[PRUEBA 1] Verificando registro de usuarios...")
        with self.app.app_context():
            u = Usuario(
                email='cliente@test.com', 
                nombre='Cliente Test', 
                password=generate_password_hash('123'), 
                rol='cliente', 
                telefono='5512345678'
            )
            db.session.add(u)
            db.session.commit()
            
            user_db = Usuario.query.filter_by(email='cliente@test.com').first()
            self.assertEqual(user_db.telefono, '5512345678')
            print(" [EXITO] Usuario y teléfono guardados correctamente.")

    # --- PRUEBA 2: MODELO HÍBRIDO (PRODUCTOS VS SERVICIOS) ---
    def test_tipos_item(self):
        print("\n[PRUEBA 2] Verificando soporte para Servicios...")
        with self.app.app_context():
            # Crear una tienda ficticia para asignar los productos
            tienda = Usuario(email='tienda@test.com', nombre='Tienda', password='123', rol='tienda')
            db.session.add(tienda)
            db.session.commit()
            
            p1 = Producto(nombre='Coca Cola', tipo='producto', precio=10, tienda_id=tienda.id)
            s1 = Producto(nombre='Plomería', tipo='servicio', precio=500, tienda_id=tienda.id)
            db.session.add_all([p1, s1])
            db.session.commit()
            
            prod = Producto.query.filter_by(nombre='Coca Cola').first()
            serv = Producto.query.filter_by(nombre='Plomería').first()
            
            self.assertEqual(prod.tipo, 'producto')
            self.assertEqual(serv.tipo, 'servicio')
            print(" [EXITO] El sistema distingue correctamente entre Productos y Servicios.")

    # --- PRUEBA 3: LÓGICA DE REPARTIDOR ---
    def test_visibilidad_repartidor(self):
        print("\n[PRUEBA 3] Verificando filtros del Repartidor...")
        with self.app.app_context():
            # Setup de usuarios
            rep = Usuario(email='rep@test.com', nombre='Rep', password=generate_password_hash('123'), rol='repartidor')
            cli = Usuario(email='cli@test.com', nombre='Cli', password=generate_password_hash('123'), rol='cliente')
            tienda = Usuario(email='shop@test.com', nombre='Shop', password=generate_password_hash('123'), rol='tienda')
            db.session.add_all([rep, cli, tienda])
            db.session.commit()

            # Pedido 1: ENVÍO ($100) -> VISIBLE
            p1 = Pedido(total=100, cliente_id=cli.id, estado='pendiente', tipo_entrega='envio')
            # Pedido 2: RECOGER ($50) -> INVISIBLE
            p2 = Pedido(total=50, cliente_id=cli.id, estado='pendiente', tipo_entrega='recoger')
            
            db.session.add_all([p1, p2])
            db.session.commit()

        # Login como Repartidor
        self.client.post('/auth/login', data={'email': 'rep@test.com', 'password': '123'})
        
        # Ver Dashboard
        response = self.client.get('/delivery/dashboard')
        html = response.data.decode('utf-8')

        # Validaciones
        if '100.0' in html: 
            print(" > El repartidor ve correctamente el pedido de envío.")
        else:
            self.fail("El repartidor NO ve el pedido de envío.")

        if '50.0' in html and 'Recoger' in html:
            self.fail("ERROR: El repartidor está viendo pedidos de 'Recoger en Tienda'.")
        else:
            print(" > El repartidor NO ve el pedido de recoger (Correcto).")

        print(" [EXITO] Filtros de logística funcionando.")

    # --- PRUEBA 4: SEGURIDAD (RBAC) ---
    def test_seguridad_dashboard(self):
        print("\n[PRUEBA 4] Seguridad: Cliente intentando entrar a Tienda...")
        # Intentar entrar con un usuario cliente a una zona protegida de tienda
        self.client.post('/auth/registro', data={'email': 'hacker@test.com', 'nombre': 'H', 'password': '123', 'rol': 'cliente', 'telefono':'00'}, follow_redirects=True)
        self.client.post('/auth/login', data={'email': 'hacker@test.com', 'password': '123'}, follow_redirects=True)
        
        response = self.client.get('/inventario/dashboard', follow_redirects=True)
        
        # Verificar que no cargó el dashboard
        self.assertNotIn(b'Panel de Control', response.data)
        print(" [EXITO] Acceso denegado correctamente.")

if __name__ == '__main__':
    print("============================================")
    print("              SUITE DE PRUEBAS")
    print("============================================")
    unittest.main(verbosity=0)