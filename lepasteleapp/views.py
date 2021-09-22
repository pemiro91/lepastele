from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

from lepasteleapp.models import (User, Producto, Pedido, Operacion, Categoria_Producto)
from django.db import transaction
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# --------------Panel de control----------------#
# ----------------------------------------------#
def login_user(request):
    if request.POST:
        form = AuthenticationForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # messages.success(request, 'Usuario autenticado satisfactoriamente.')
                return redirect('panel')
        else:
            messages.error(request, 'Usuario o contraseña incorrecto.')
            return redirect('login_user')
    else:
        form = AuthenticationForm()
    return render(request, 'control_panel/login.html', {'form': form})


def logout(request):
    do_logout(request)
    return redirect('login_user')


def panel_home(request):
    if request.user.is_authenticated:
        operaciones_del_dia = Operacion.objects.all()
        context = {'operaciones_del_dia': operaciones_del_dia}
        return render(request, "control_panel/index.html", context)
    return redirect('login_user')


#
# -----------------CRDU Categorias de Piezas---------------------------#
def categorias_productos(request):
    if request.user.is_authenticated:
        categorias_productos = Categoria_Producto.objects.all()
        context = {'categorias_productos': categorias_productos}
        return render(request,
                      "control_panel/gestion_del_sitio/productos/categorias_productos/categorias_productos.html",
                      context)
    return redirect('login_user')


def agregar_categoria_producto(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            nombre_categoria = request.POST.get('nombre_categoria')
            descripcion_categoria = request.POST.get('descripcion_categoria')

            c = Categoria_Producto.objects.create(
                nombre_categoria=nombre_categoria,
                descripcion=descripcion_categoria
            )
            c.save()
            messages.success(request, 'La categoría fue registrada satisfactoriamente')
            return redirect('categorias_productos')

        context = {}
        return render(request,
                      "control_panel/gestion_del_sitio/productos/categorias_productos/insertar_categ_producto.html",
                      context)
    return redirect('login_user')


def modificar_categoria_producto(request, id_cp=None):
    if request.user.is_authenticated:
        categoria_producto = Categoria_Producto.objects.get(id=id_cp)
        # notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        # cant_notificaciones = len(notificaciones)
        if request.method == 'POST':
            nombre_categoria = request.POST.get('nombre_categoria')
            descripcion_categoria = request.POST.get('descripcion_categoria')

            Categoria_Producto.objects.filter(id=id_cp).update(
                nombre_categoria=nombre_categoria,
                descripcion=descripcion_categoria)

            messages.success(request, 'La categoría de pieza fue editada satisfactoriamente')
            return redirect('categorias_productos')
        context = {'categoria_producto': categoria_producto}
        return render(request,
                      'control_panel/gestion_del_sitio/productos/categorias_productos'
                      '/modificar_categoria_producto.html',
                      context)
    return redirect('login_user')


def eliminar_categoria_producto(request, id_cp):
    if request.user.is_authenticated:
        cp = Categoria_Producto.objects.get(id=id_cp)
        cp.delete()
        return redirect('categorias_productos')
    return redirect('login_user')


# -----------------CRDU Piezas----------------------------------------#
def productos(request):
    productos = Producto.objects.all()
    context = {'productos': productos}
    return render(request, "control_panel/gestion_del_sitio/productos/productos.html", context)


def agregar_producto(request):
    if request.method == 'POST':
        productoForm = ProductoForm(request.POST or None, request.FILES or None)
        if productoForm.is_valid():
            producto_form = productoForm.save(commit=False)
            producto_form.save()
            messages.success(request,
                             "El producto se agregó satisfactoriamente!")
            return redirect("productos")
        else:
            print(productoForm.errors)
    else:
        productoForm = ProductoForm()
    return render(request, 'control_panel/gestion_del_sitio/productos/insertar_producto.html',
                  {'productoForm': productoForm})


def modificar_producto(request, id_p=None):
    if request.user.is_authenticated:
        producto_custom = Producto.objects.get(id=id_p)
        # notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        # cant_notificaciones = len(notificaciones)
        update_form = ProductoForm(request.POST or None, request.FILES or None, instance=producto_custom)
        if update_form.is_valid():
            edit = update_form.save(commit=False)
            edit.save()
            messages.success(request, 'Prodcuto modificado correctamente')
            return redirect('productos')
        context = {'producto': producto_custom, 'update_form': update_form, }
        return render(request,
                      'control_panel/gestion_del_sitio/productos/modificar_productos.html',
                      context)
    return redirect('login_user')


def eliminar_producto(request, id_p):
    if request.user.is_authenticated:
        p = Producto.objects.get(id=id_p)
        p.delete()
        messages.success(request, 'Prodcuto eliminado satisfactoriamente')
        return redirect('productos')
    return redirect('login_user')


# --------------- CRUD Operaciones----------------------#


def operaciones(request):
    operaciones = Operacion.objects.all()
    context = {'operaciones': operaciones}
    return render(request,
                  "control_panel/gestion_del_sitio/operaciones/operaciones.html", context)


def registrar_venta(request):
    # if request.user.is_authenticated:
    #     if request.method == "POST":
    #         nombre_categoria = request.POST.get('nombre_categoria')
    #         descripcion_categoria = request.POST.get('descripcion_categoria')
    #
    #         c = Categoria_Producto.objects.create(
    #             nombre_categoria=nombre_categoria,
    #             descripcion=descripcion_categoria
    #         )
    #         c.save()
    #         messages.success(request, 'La categoría fue registrada satisfactoriamente')
    #         return redirect('categorias_productos')
    #
    #     context = {}
    #     return render(request,
    #                   "control_panel/gestion_del_sitio/productos/categorias_productos/insertar_categ_producto.html",
    #                   context)
    # return redirect('login_user')
    context = {}
    return render(request,
                  "control_panel/gestion_del_sitio/operaciones/registrar_operacion.html",
                  context)

# --------------- Gestion de Usuarios----------------------#


def usuarios(request):
    usuarios = User.objects.filter().exclude(username=request.user.username).exclude(is_superuser=1)
    context = {'usuarios': usuarios}
    return render(request, "control_panel/gestion_de_usuarios/usuarios.html", context)


def insertar_usuario(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            genero = request.POST.get('sexo')
            user_name = request.POST.get('user_name')
            rol_de = request.POST.get('rol_de')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if User.objects.filter(username=user_name).exists():
                messages.warning(request, 'El nombre de usuario ya existe, por favor defina otronombre de usuario')
                return redirect('insertar_usuarios')
            elif password1 != password2:
                messages.warning(request,
                                 'Las contraseñas no coinciden, por favor escriba correctamente la contraseña')
                return redirect('insertar_usuarios')
            else:
                if rol_de == 'dependiente':
                    user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        username=user_name,
                        is_dependiente = True,
                        is_moderador=False,
                        is_administrador=False,
                        sexo=genero
                    )
                    user.save()
                    # messages.success(request, 'Usuario registrado satisfactoriamente')
                    # return redirect('usuarios')
                elif rol_de == 'moderador':
                    user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        username=user_name,
                        is_dependiente=False,
                        is_moderador=True,
                        is_administrador=False,
                        sexo=genero
                    )
                    user.save()

                else:
                    user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        username=user_name,
                        is_dependiente=False,
                        is_moderador=False,
                        is_administrador=True,
                        sexo=genero
                    )
                    user.save()
                    # messages.success(request, 'Usuario registrado satisfactoriamente')
                    # return redirect('usuarios')

            # Agregando el mensaje de notificacion en la base de datos
            # mensaje_notificacion = 'El usuario: ' + user.username + ' se agregó correctamente'
            # if mensaje_notificacion != '':
            #     notificacion = Notification(mensaje=mensaje_notificacion, usuario=request.user,
            #                                 estado='No-Leido', tipo='Usuario')
            #     notificacion.save()
            messages.success(request, 'Usuario registrado satisfactoriamente')
            return redirect('usuarios')
        context = {}
        return render(request, 'control_panel/gestion_de_usuarios/insertar_usuarios.html', context)
    return redirect('login_user')


def editar_usuario(request, id_user=None):
    if request.user.is_authenticated:
        user_custom = User.objects.get(id=id_user)
        # notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        # cant_notificaciones = len(notificaciones)
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            genero = request.POST.get('sexo')
            user_name = request.POST.get('user_name')
            rol_de = request.POST.get('rol_de')
            password1 = request.POST.get('password1')
            with transaction.atomic():
                user_custom.set_password(password1)
                user_custom.save()
                if rol_de == 'moderador':
                    User.objects.filter(id=id_user).update(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        username=user_name,
                        is_moderador=True,
                        is_administrador=False,
                        sexo=genero
                    )
                else:
                    User.objects.filter(id=id_user).update(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        username=user_name,
                        is_moderador=False,
                        is_administrador=True,
                        sexo=genero
                    )
            messages.success(request, 'Datos de usuario actualizado satisfactoriamente')
            return redirect('usuarios')
        context = {'user': user_custom}
        return render(request, 'control_panel/gestion_de_usuarios/editar_usuarios.html', context)
    return redirect('login_user')


def eliminar_usuario(request, id_user):
    if request.user.is_authenticated:
        u = User.objects.get(id=id_user)
        u.delete()
        return redirect('usuarios')
    return redirect('login_user')
