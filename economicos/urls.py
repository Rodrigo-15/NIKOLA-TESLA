from django.urls import path, include
from .router import router
from .views import *

urlpatterns = [
    path("", include(router.urls)),
    path("import_pagos/", import_pagos, name="import_pagos"),
    path("pagos-filter/", filter_pago, name="pagos-filter"),
    path("pagos-sin-conciliar/", filter_pago_sin_conciliar,
         name="pagos-sin-conciliar"),
    path("conciliar_pagos/", conciliar_pagos, name="conciliar_pagos"),
    path("pagos_generate/", pago_generate,{'id_pago':None}, name="pagos_generate"),
    path("pagos_generate/<int:id_pago>", pago_generate, name="pagos_generate"),
    path("get_dashboard/", get_dashboard, name="get_dashboard"),
    path("save_pago/", save_pago, name="save_pago"),
]
