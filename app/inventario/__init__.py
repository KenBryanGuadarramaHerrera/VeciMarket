from flask import Blueprint

inventario = Blueprint('inventario', __name__)

from . import routes