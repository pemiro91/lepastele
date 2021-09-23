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
    path('panel/operaciones', views.operaciones, name="operaciones"),
    path('panel/operaciones/registrar_venta', views.registrar_venta, name="registrar_venta"),
    path('panel/operaciones/detalles_de_venta', views.detalles_de_operacion, name="detalles_operacion"),
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
