from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

from lepasteleapp.models import *
from django.db import transaction
# from .forms import *
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


# -----------------CRDU Categorias de Piezas---------------------------#
def categorias_piezas(request):
    if request.user.is_authenticated:
        categorias_piezas = Categoria_Producto.objects.all()
        context = {'categorias_productos': categorias_piezas}
        return render(request,
                      "control_panel/gestion_de_operaciones/productos/categorias_productos/categorias_piezas.html",
                      context)
    return redirect('login_user')


def agregar_categoria_pieza(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            nombre_categoria = request.POST.get('nombre_categoria')
            descripcion_categoria = request.POST.get('descripcion_categoria')
            tipo_pieza = request.POST.get('tipo_pieza')

            c = Categoria_Producto.objects.create(
                nombre_categoria=nombre_categoria,
                descripcion=descripcion_categoria,
                tipo_pieza=tipo_pieza
            )
            c.save()
            messages.success(request, 'La categoría de pieza fue registrada satisfactoriamente')
            return redirect('categorias_piezas')

        context = {}
        return render(request,
                      "control_panel/gestion_de_operaciones/productos/categorias_productos/insertar_categ_pieza.html",
                      context)
    return redirect('login_user')


def modificar_categoria_pieza(request, id_cp=None):
    if request.user.is_authenticated:
        categoria_pieza_custom = Categoria_Producto.objects.get(id=id_cp)
        # notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        # cant_notificaciones = len(notificaciones)
        if request.method == 'POST':
            nombre_categoria = request.POST.get('nombre_categoria')
            descripcion_categoria = request.POST.get('descripcion_categoria')
            tipo_pieza = request.POST.get('tipo_pieza')

            Categoria_Producto.objects.filter(id=id_cp).update(
                nombre_categoria=nombre_categoria,
                descripcion=descripcion_categoria,
                tipo_pieza=tipo_pieza
            )
            messages.success(request, 'La categoría de pieza fue editada satisfactoriamente')
            return redirect('categorias_piezas')
        context = {'categoria_pieza': categoria_pieza_custom}
        return render(request,
                      'control_panel/gestion_de_operaciones/productos/categorias_productos/modificar_categoria_piezas.html',
                      context)
    return redirect('login_user')


def eliminar_categoria_pieza(request, id_cp):
    if request.user.is_authenticated:
        cp = Categoria_Producto.objects.get(id=id_cp)
        cp.delete()
        return redirect('categorias_piezas')
    return redirect('login_user')


# -----------------CRDU Piezas----------------------------------------#
def piezas(request):
    piezas = Producto.objects.all()
    context = {'productos': piezas}
    return render(request, "control_panel/gestion_de_operaciones/productos/operacion.html", context)


def agregar_pieza(request):
    ImageFormSet = modelformset_factory(Imagenes,
                                        form=ImagenForm, extra=4)
    # 'extra' means the number of photos that you can upload
    if request.method == 'POST':
        pieceForm = PiezaForm(request.POST or None, request.FILES or None)
        formset = ImageFormSet(request.POST or None, request.FILES or None,
                               queryset=Imagenes.objects.none())
        if pieceForm.is_valid() and formset.is_valid():
            piece_form = pieceForm.save(commit=False)
            # piece_form.user = request.user
            piece_form.save()

            for form in formset.cleaned_data:
                # this helps to not crash if the user
                # do not upload all the photos
                if form:
                    imagen = form['imagen']
                    # imagen_principal = form['imagen_principal']
                    photo = Imagenes(pieza=piece_form, imagen=imagen)
                    photo.save()
            # use django messages framework
            messages.success(request,
                             "La pieza se agregó satisfactoriamente!")
            return redirect("piezas")
        else:
            print(pieceForm.errors, formset.errors)
    else:
        pieceForm = PiezaForm()
        formset = ImageFormSet(queryset=Imagenes.objects.none())
    return render(request, 'control_panel/gestion_de_operaciones/productos/insertar_operacion.html',
                  {'pieceForm': pieceForm, 'formset': formset})


def modificar_pieza(request, id_p=None):
    if request.user.is_authenticated:
        pieza_custom = Producto.objects.get(id=id_p)
        # notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        # cant_notificaciones = len(notificaciones)
        update_form = PiezaForm(request.POST or None, request.FILES or None, instance=pieza_custom)
        if update_form.is_valid():
            edit = update_form.save(commit=False)
            edit.save()
            messages.success(request, 'Pieza modificada correctamente')
            return redirect('piezas')
        context = {'pieza': pieza_custom, 'update_form': update_form, }
        return render(request,
                      'control_panel/gestion_de_operaciones/productos/modificar_operacion.html',
                      context)
    return redirect('login_user')


def eliminar_pieza(request, id_p):
    if request.user.is_authenticated:
        p = Producto.objects.get(id=id_p)
        p.delete()
        return redirect('piezas')
    return redirect('login_user')


# --------------- CRUD Operaciones----------------------#


def operaciones(request):
    operaciones = Operacion.objects.all()
    context = {'operaciones': operaciones}
    return render(request,
                  "control_panel/gestion_de_operaciones/operaciones/operaciones.html", context)


def certificado_pieza(request, id_cp=None):
    certificado_pieza = Certificacion_GAM.objects.get(id=id_cp)
    imagenes = Imagenes.objects.filter(pieza=certificado_pieza.pieza.id)
    context = {'certificado_GAM_pieza': certificado_pieza,
               'imagenes': imagenes}
    return render(request,
                  "control_panel/gestion_de_operaciones/operaciones/detalles_de_operacion.html", context)


def modificar_certificado_pieza(request):
    context = {}
    return render(request,
                  "control_panel/gestion_de_operaciones/operaciones/modificar_certificado_pieza_GAM.html",
                  context)


def agregar_certificacion_pieza_por_GAM(request):
    if request.method == 'POST':
        certificacion_GAM = Certificacion_GAMForm(request.POST or None)
        # formset = ImageFormSet(request.POST or None, request.FILES or None,
        #                        queryset=Imagenes.objects.none())
        if certificacion_GAM.is_valid():
            certificacion_GAM = certificacion_GAM.save(commit=False)
            # piece_form.user = request.user
            certificacion_GAM.save()

            messages.success(request,
                             "La certificación por GAM de la pieza se agregó satisfactoriamente!")
            return redirect("certificados_por_GAM")
        else:
            print(certificacion_GAM.errors)
    else:
        certificacion_GAM = Certificacion_GAMForm()
    return render(request, 'control_panel/gestion_de_operaciones/operaciones/realizar_operacion.html',
                  {'certificacion_GAMForm': certificacion_GAM})

    # --------------- CRUD Categoria de Publicaciones----------------------#


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
                if rol_de == 'moderador':
                    user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        username=user_name,
                        is_moderador=True,
                        is_administrador=False,
                        sexo=genero
                    )
                    user.save()
                    # messages.success(request, 'Usuario registrado satisfactoriamente')
                    # return redirect('usuarios')

                else:
                    user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        username=user_name,
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
