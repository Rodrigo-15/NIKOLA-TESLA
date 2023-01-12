# import router
from rest_framework_bulk.routes import BulkRouter
from .viewsets import *

router = BulkRouter()
router.register(r"conceptos", ConceptoViewSet)
router.register(r"pagos", PagoViewSet) 
