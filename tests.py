import unittest
from app import create_app, db
from app.models import Usuario, Producto

class VeciMarketTestCase(unittest.TestCase):
    
    def setUp(self):
        
        # Pasamos la configuración para que create_app use memoria DESDE EL INICIO.
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True,
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()
        
        # Ahora sí, creamos tablas en la memoria RAM
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all() # Esto ahora solo borra la RAM, no el archivo.

    def test_creacion_usuario(self):
        print("\n[PRUEBA 1] Verificando registro de usuarios en base de datos...")
        with self.app.app_context():
            u = Usuario(email='tienda@test.com', nombre='Tienda Test', password='123', rol='tienda')
            db.session.add(u)
            db.session.commit()
            
            busqueda = Usuario.query.filter_by(email='tienda@test.com').first()
            self.assertIsNotNone(busqueda)
            self.assertEqual(busqueda.rol, 'tienda')
            print(" [EXITO] Usuario creado en memoria.")

    def test_logica_stock(self):
        print("\n[PRUEBA 2] Verificando lógica matemática del inventario...")
        with self.app.app_context():
            dueño = Usuario(email='dueño@test.com', nombre='Dueño', password='123', rol='tienda')
            db.session.add(dueño)
            db.session.commit()
            
            producto = Producto(nombre='Coca Cola', precio=15.0, stock_actual=10, stock_minimo=5, tienda_id=dueño.id)
            db.session.add(producto)
            db.session.commit()
            
            producto.stock_actual -= 3
            db.session.commit()
            
            p_actualizado = Producto.query.filter_by(nombre='Coca Cola').first()
            self.assertEqual(p_actualizado.stock_actual, 7)
            print(" [EXITO] Cálculo correcto.")

    def test_landing_page(self):
        print("\n[PRUEBA 3] Verificando Landing Page...")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        if b'VeciMarket' in response.data:
            print(" [EXITO] Página carga OK.")

    def test_acceso_dashboard_sin_login(self):
        print("\n[PRUEBA 4] Seguridad: Acceso anónimo...")
        response = self.client.get('/inventario/dashboard', follow_redirects=True)
        self.assertIn(b'Iniciar', response.data)
        print(" [EXITO] Bloqueo verificado.")

    def test_cliente_no_entra_a_tienda(self):
        print("\n[PRUEBA 5] Seguridad (RBAC): Cliente a Tienda...")
        self.client.post('/auth/registro', data={'email': 'hacker@test.com', 'nombre': 'Hacker', 'password': '123', 'rol': 'cliente'}, follow_redirects=True)
        self.client.post('/auth/login', data={'email': 'hacker@test.com', 'password': '123'}, follow_redirects=True)
        
        response = self.client.get('/inventario/dashboard', follow_redirects=True)
        
        if b'Acceso denegado' in response.data or b'Panel de Control' not in response.data:
            print(" [EXITO] Acceso denegado correctamente.")
        else:
            self.fail("El cliente pudo entrar al dashboard.")

if __name__ == '__main__':
    unittest.main(verbosity=0)