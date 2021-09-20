"""LePastele URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

    # # -----------------Gestion del Sitio-----------------
    # # Crud Categorias de Productos
    # path('panel/productos/categorias', views.categorias_piezas, name="categorias_productos"),
    # path('panel/productos/insertar_categoria_pieza', views.agregar_categoria_pieza, name="insertar_categoria_pieza"),
    # path('panel/productos/editar_categoria_pieza/<int:id_cp>', views.modificar_categoria_pieza,
    #      name="editar_categoria_pieza"),
    # path('panel/productos/eliminar_categoria_pieza/<int:id_cp>', views.eliminar_categoria_pieza,
    #      name="eliminar_categoria_pieza"),
    #
    # # Crud de Productos
    # path('panel/productos', views.piezas, name="productos"),
    # path('panel/productos/insertar_pieza', views.agregar_pieza, name="insertar_pieza"),
    # path('panel/productos/editar_pieza/<int:id_p>', views.modificar_pieza, name="editar_pieza"),
    # path('panel/productos/eliminar_pieza/<int:id_p>', views.eliminar_pieza,
    #      name="eliminar_pieza"),
    #
    # # Crud de Operaciones
    # path('panel/operaciones', views.operaciones, name="certificados_por_GAM"),
    # path('panel/servicios/certificados_por_GAM/certificado_pieza/<int:id_cp>', views.certificado_pieza,
    #      name="certificado_pieza"),
    # path('panel/servicios/certificados_por_GAM/modificar_certificacdo_pieza', views.modificar_certificado_pieza,
    #      name="modificar_certificado_pieza"),
    # path('panel/productos/agregar_certificacion_por_GAM', views.agregar_certificacion_pieza_por_GAM,
    #      name="agregar_certificacion_por_GAM"),
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

