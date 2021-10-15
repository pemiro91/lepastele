from django.contrib import admin
from django.urls import path
from lepasteleapp import views
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # ------------------Panel de Administración-----------
    path('', views.login_user, name="login_user"),
    path('salir', views.logout, name="salir"),
    path('panel', views.panel_home, name="panel"),

    # -----------------Gestion del Sitio-----------------
    # Crud Categorias de Productos
    path('panel/productos/categorias', views.categorias_productos, name="categorias_productos"),
    path('panel/productos/insertar_categoria_producto', views.agregar_categoria_producto,
         name="insertar_categoria_producto"),
    path('panel/productos/editar_categoria_producto/<int:id_cp>', views.modificar_categoria_producto,
         name="editar_categoria_producto"),
    path('panel/productos/eliminar_categoria_producto/<int:id_cp>', views.eliminar_categoria_producto,
         name="eliminar_categoria_producto"),

    # Crud de Productos
    path('panel/productos', views.productos, name="productos"),
    path('panel/productos/insertar_producto', views.agregar_producto, name="insertar_producto"),
    path('panel/productos/editar_producto/<int:id_p>', views.modificar_producto, name="editar_producto"),
    path('panel/productos/eliminar_producto/<int:id_p>', views.eliminar_producto,
         name="eliminar_producto"),
    #
    # # Crud de Operaciones
    path('panel/operaciones', views.operaciones_dia, name="operaciones"),
    path('panel/operaciones_general', views.operaciones_general, name="operaciones_general"),
    path('panel/operaciones/punto_venta_categoria', views.punto_venta_categoria, name="punto_venta_categoria"),
    path('panel/operaciones/add_spending', views.add_spending, name="add_spending"),
    path('panel/operaciones/punto_venta', views.punto_venta, name="punto_venta"),
    path('panel/operaciones/add_order/<int:id_p>', views.add_order, name="add_order"),
    path('panel/operaciones/carrito', views.carrito, name="carrito"),
    path('panel/operaciones/edit_order/<int:id_o>', views.edit_order, name="edit_order"),
    path('panel/operaciones/delete_order/<int:id_o>', views.delete_order, name="delete_order"),
    path('panel/operaciones/pagar', views.sales_order, name="pagar"),
    path('panel/operaciones/pagar_transfer', views.sales_order_transfer, name="pagar_transfer"),
    path('panel/operaciones/pago_confirmado/<int:id_op>', views.pago_confirmado, name="pago_confirmado"),
    path('panel/operaciones/abrir_venta', views.abrir_caja, name="abrir_venta"),
    path('panel/operaciones/cerrar_caja', views.cerrar_caja, name="cerrar_caja"),
    path('panel/operaciones/cerrar_venta', views.cerrar_venta, name="cerrar_venta"),
    path('panel/operaciones/detalles_de_venta/<int:id_op>', views.detalles_de_operation, name="detalles_operation"),
    path('panel/operaciones/detalles_de_operation_general/<int:id_op>',
         views.detalles_de_operation_general, name="detalles_de_operation_general"),
    path('panel/operaciones/factura_general/<int:id_opg>/<int:id_op>', views.factura_general, name="factura_general"),
    path('panel/operaciones/factura_resumen/<int:id_op>', views.factura_resumen, name="factura_resumen"),
    path('panel/operaciones/gastos_dia', views.gastos_dia, name="gastos_dia"),
    path('panel/operaciones/gastos_general', views.gastos_general, name="gastos_general"),
    path('panel/operaciones/gastos_general/detalle_gasto/<int:id_gg>', views.gastos_dia_general,
         name="gastos_dia_general"),
    path('panel/operaciones/charge_order', views.charge_order, name="charge_order"),
    #
    # ----------------------Gestion de Usuarios-------------------------
    # Crud Usuarios
    path('panel/usuarios', views.usuarios, name="usuarios"),
    path('panel/insertar_usuario', views.insertar_usuario, name="insertar_usuario"),
    path('panel/editar_usuario/<int:id_user>', views.editar_usuario, name="editar_usuario"),
    path('panel/eliminar_usuario/<int:id_user>', views.eliminar_usuario, name="eliminar_usuario"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
