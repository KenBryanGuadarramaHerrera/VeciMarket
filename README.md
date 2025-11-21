# VeciMarket: Plataforma de Comercio Hiperlocal y Última Milla

Este proyecto implementa una solución integral de comercio electrónico "Hiperlocal" utilizando **Python (Flask)**. El sistema está diseñado para digitalizar la economía de barrio, conectando tres actores clave: Comercios Locales, Vecinos (Clientes) y Repartidores. La arquitectura se basa en un diseño modular mediante **Blueprints**, simulando microservicios lógicos para garantizar escalabilidad, seguridad basada en roles (RBAC) y una gestión eficiente de inventarios y logística de última milla.

---

## Características Principales
* **Arquitectura Modular:** Uso de Flask Blueprints para separar la lógica de Tienda, Cliente, Repartidor y Autenticación.
* **Modelo de Negocio Híbrido:** Soporte diferenciado para **Productos** (con control de stock y envío) y **Servicios** (con contacto directo vía WhatsApp).
* **Gestión Inteligente de Inventario:** Dashboard para tiendas con alertas automáticas de stock crítico y gráficas de rendimiento.
* **Logística Visual:** Integración de **Leaflet.js** para visualización de rutas y mapas interactivos para repartidores.
* **Diseño "VeciMarket Pro":** Interfaz moderna y responsiva (CSS nativo, sin dependencias pesadas como Bootstrap).
* **Control de Calidad (QA):** Suite de pruebas automatizadas (`unittest`) para validar lógica de negocio y seguridad.

---

##  Arquitectura del Proyecto

El sistema sigue una arquitectura **MVC (Modelo-Vista-Controlador)** modularizada. A continuación se describe la estructura de carpetas y archivos:

```text
/marketplace_proyecto
│
├── run.py                  # [ENTRY POINT] Punto de entrada. Inicia el servidor WSGI
│                           # y levanta la aplicación Flask.
│
├── config.py               # [CONFIG] Variables de entorno, llaves secretas y
│                           # configuración de la base de datos.
│
├── tests.py                # [QA] Suite de pruebas automatizadas. Verifica integridad
│                           # de datos, seguridad de roles y flujos de compra.
│
├── requirements.txt        # [DEPENDENCIAS] Lista de librerías (Flask, SQLAlchemy, etc.).
│
└── app/
    ├── __init__.py         # [FACTORY] Inicializa la app, BD y registra Blueprints.
    ├── models.py           # [MODELO] Esquema de Base de Datos Relacional. Define
    │                       # Usuarios, Productos, Pedidos e Items.
    │
    ├── static/             # [ASSETS] CSS personalizado, JS y carpeta 'uploads' para imágenes.
    │
    ├── templates/          # [VISTA] Interfaz de Usuario (HTML + Jinja2).
    │   ├── base.html       # Layout maestro dinámico.
    │   ├── landing.html    # Página de inicio y propuesta de valor.
    │   ├── auth/           # Vistas de Login y Registro.
    │   ├── market/         # Catálogo, Filtros, Carrito e Historial.
    │   ├── inventario/     # Dashboard de gestión para Tiendas.
    │   └── delivery/       # Panel de control para Repartidores.
    │
    │   # --- MÓDULOS (CONTROLADORES/BLUEPRINTS) ---
    ├── auth/               # Gestión de Identidad y Sesiones.
    ├── market/             # Lógica de compra, catálogo y checkout.
    ├── inventario/         # Lógica de negocio para tiendas (Stock/Ventas).
    └── delivery/           # Lógica logística y asignación de pedidos.
```
---

### Relación entre módulos

1.  **`auth` (Guardián):** Gestiona el acceso. Determina si el usuario es `cliente`, `tienda` o `repartidor` y redirige al módulo correspondiente.
2.  **`inventario` (Proveedor):** Permite a las tiendas poblar la base de datos. Define si un ítem es un producto físico (requiere envío) o un servicio (requiere contacto).
3.  **`market` (Consumidor):** Consume los datos de `inventario`. Gestiona el carrito de compras y genera las órdenes en la base de datos (Tabla `Pedido`).
4.  **`delivery` (Logística):** Escucha la tabla `Pedido`. Si un pedido es de tipo "envío", lo muestra en el tablero de repartidores disponibles para ser aceptado.
---

## Fundamentos Técnicos

El sistema implementa lógicas de negocio complejas para asegurar la consistencia:

1.  **Role-Based Access Control (RBAC)** Decoradores personalizados (`@solo_tiendas`, `@login_required`) aseguran que un cliente no pueda acceder al panel de inventario, ni un repartidor al carrito de compras.
2.  **Transaccionalidad:** El descuento de stock ocurre atómicamente al confirmar el pedido. Si es un servicio, se omite la lógica de stock.
3.  **Persistencia Relacional:** Uso de SQLAlchemy para manejar relaciones complejas: `Usuario` (Tienda) -> `Producto` -> `PedidoItem` -> `Pedido` -> `Usuario` (Cliente/Repartidor).
4.  **Testing Aislado:** Las pruebas (`tests.py`) se ejecutan en una base de datos en memoria (`sqlite:///:memory:`) para no corromper los datos de producción.


---

##  Requisitos Previos

* **Python 3.** o superior.
* **Pip** (Gestor de paquetes de Python).

---

##  Instalación y Ejecución

Sigue estos pasos para desplegar el proyecto localmente:

### 1. Clonar el repositorio
Descarga el código fuente o clona este repositorio.

### 2. Instalar dependencias
Navega a la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar Pruebas
Verifica que la lógica del sistema esta íntegra antes de iniciar:
```bash
python tests.py
```

### 4. Ejecutar el Servidor
Inicia la aplicación Flask:
```bash
python run.py
```
### 4. Acceder
Abre tu navegador web e ingresa a:
`http://127.0.0.1:5000`

---

##  Flujo de Uso

1. **Tienda (Oferta):** 
   * Regístrese seleccionando el rol "Negocio".
   * Acceda al Dashboard y use "Nuevo Producto".
   * Seleccione si ofrece un Producto (controla stock) o un Servicio (fontanería, clases, etc.).
   * Suba una imagen y defina el precio y demas parámetros del producto o servicio.
     
2. **Cliente (Demanda):**
   * Regístrese como "Cliente".
   * Navegue por el catálogo. Use las pestañas para filtrar entre Productos y Servicios.
   * **Si es Producto:** Agréguelo al carrito y proceda al pago (Checkout). Seleccione envío o recoger en tienda.
   * **Si es Servicio:** Use el botón de WhatsApp para contactar al proveedor directamente.
     
3. **Repartidor (Logística):**
   * Regístrese como "Repartidor".
   * En su panel verá las "Nuevas Solicitudes" (Solo pedidos de productos con envío a domicilio).
   * Acepte un pedido para ver el mapa de ruta y el contacto del cliente.
   * Marque el pedido como "Entregado" para finalizar el ciclo.


---
