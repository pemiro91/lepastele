from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from datetime import datetime, date, timedelta

from lepasteleapp.models import (User, Producto, Pedido, Operacion, FacturaFinal,
                                 Categoria_Producto, Historial, CerrarOperacion, OperacionGeneral, OperacionDia)
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


def base_admin(request):
    if request.user.is_authenticated:
        user = request.user
        operaciones_del_dia = Operacion.objects.all()
        operacionesGeneral = OperacionGeneral.objects.all()
        context = {'operaciones_del_dia': operaciones_del_dia, 'operaciones_general': operacionesGeneral, 'user': user}
        return render(request, "control_panel/base_admin.html", context)
    return redirect('login_user')


def panel_home(request):
    if request.user.is_authenticated:
        operaciones_generales = OperacionGeneral.objects.all()
        total_operaciones = 0
        monto_total = 0.0
        propina_total = 0.0
        for opg in operaciones_generales:
            total_operaciones += opg.operaciones.count()
            monto_total += opg.monto_total_dia
            propina_total += opg.propina_total_dia
        users = User.objects.filter(is_superuser=False).all()
        products = Producto.objects.all()
        operacionesDia = Operacion.objects.filter(usuario=request.user).order_by('-id')[:7]
        isClose = CerrarOperacion.objects.all().last()
        context = {'products': products, 'total_operaciones': total_operaciones,
                   'usuarios': users, 'monto_total': monto_total, 'cerrarOperation': isClose,
                   'propina_total': propina_total, 'operacionesDia': operacionesDia}
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
        update_form = ProductoForm(request.POST or None, request.FILES or None, instance=producto_custom)
        if update_form.is_valid():
            edit = update_form.save(commit=False)
            edit.save()
            messages.success(request, 'Producto modificado correctamente')
            return redirect('productos')
        context = {'producto': producto_custom, 'update_form': update_form, }
        return render(request, 'control_panel/gestion_del_sitio/productos/modificar_productos.html', context)
    return redirect('login_user')


def eliminar_producto(request, id_p):
    if request.user.is_authenticated:
        p = Producto.objects.get(id=id_p)
        p.delete()
        messages.success(request, 'Producto eliminado satisfactoriamente')
        return redirect('productos')
    return redirect('login_user')

# --------------- CRUD Operaciones----------------------#


def operaciones_dia(request):
    operations = Operacion.objects.all()
    total_dia = 0.0
    propina_dia = 0.0
    for ope in operations:
        total_dia += ope.monto_total_a_pagar
        if ope.propina_del_cliente is None:
            propina_dia += 0.0
        else:
            propina_dia += ope.propina_del_cliente
    isClose = CerrarOperacion.objects.all().last()
    context = {'operaciones': operations, 'total_dia': total_dia, 'propina_dia': propina_dia,
               'cerrarOperation': isClose}
    return render(request, "control_panel/gestion_del_sitio/operaciones/ventas_dia.html", context)


class Ventas:
    def __init__(self, id, monto_total_dia, propina_total_dia, cantidadVentas, fecha_operacion):
        self.id = id
        self.monto_total_dia = monto_total_dia
        self.propina_total_dia = propina_total_dia
        self.cantidadVentas = cantidadVentas
        self.fecha_operacion = fecha_operacion


def operaciones_general(request):
    operationsGeneral = OperacionGeneral.objects.all()
    total_venta_general = 0.0
    propina_general = 0.0
    listCantidadVentas = []
    for o in operationsGeneral:
        cantidadVentas = OperacionDia.objects.filter(fecha_operacion__year=o.fecha_operacion.year,
                                                     fecha_operacion__month=o.fecha_operacion.month,
                                                     fecha_operacion__day=o.fecha_operacion.day
                                                     ).count()
        obVenta = Ventas(o.id, o.monto_total_dia, o.propina_total_dia, cantidadVentas, o.fecha_operacion)
        listCantidadVentas.append(obVenta)
    for operat in operationsGeneral:
        total_venta_general += operat.monto_total_dia
        if operat.propina_total_dia is None:
            propina_general += 0.0
        else:
            propina_general += operat.propina_total_dia
    context = {'operationsGeneral': listCantidadVentas,
               'total_venta_general': total_venta_general, 'propina_general': propina_general}
    return render(request, "control_panel/gestion_del_sitio/operaciones/ventas_general.html", context)


def detalles_de_operation_general(request, id_op):
    operation = get_object_or_404(OperacionGeneral, id=id_op)
    total_venta_general = operation.monto_total_dia
    propina_general = operation.propina_total_dia

    totalVentas = OperacionDia.objects.filter(fecha_operacion__year=operation.fecha_operacion.year,
                                              fecha_operacion__month=operation.fecha_operacion.month,
                                              fecha_operacion__day=operation.fecha_operacion.day)

    context = {
        'operation': operation,
        'total_venta_general': total_venta_general,
        'propina_general': propina_general,
        'totalVentas': totalVentas
    }
    return render(request, "control_panel/gestion_del_sitio/operaciones/detalles_operacion_general.html", context)


def abrir_venta(request):
    if request.user.is_authenticated:
        isClose = CerrarOperacion.objects.all().last()
        CerrarOperacion.objects.filter(id=isClose.id).update(is_closed=False)
        messages.success(request, 'Venta abierta satisfactoriamente')
        return redirect('punto_venta')
    return redirect('login_user')


def cerrar_venta(request):
    if request.user.is_authenticated:
        CerrarOperacion.objects.create(is_closed=True, usuario=request.user, fecha_cierre=datetime.now())
        operations_day = Operacion.objects.all()

        for oper in operations_day:
            oper_day = OperacionDia.objects.create(
                usuario=oper.usuario,
                tipo_pago=oper.tipo_pago,
                monto_total_a_pagar=oper.monto_total_a_pagar,
                monto_pagado_cliente=oper.monto_pagado_cliente,
                monto_a_devolver=oper.monto_a_devolver,
                numero_de_transferencia=oper.numero_de_transferencia,
                propina_del_cliente=oper.propina_del_cliente,
                fecha_operacion=oper.fecha_operacion
            )
            for itemOpero in oper.pedidos.all():
                factura = FacturaFinal.objects.create(producto=itemOpero.producto,
                                                      cantidad_producto=itemOpero.cantidad_producto)
                oper_day.facturas.add(factura)
        total_dia = 0.0
        total_propina = 0.0
        for ope in operations_day:
            total_dia += ope.monto_total_a_pagar
            if ope.propina_del_cliente is None:
                total_propina += 0.0
            else:
                total_propina += ope.propina_del_cliente

        operation_general = OperacionGeneral.objects.create(
            usuario=request.user,
            monto_total_dia=total_dia,
            propina_total_dia=total_propina,
            fecha_operacion=datetime.now()
        )
        listOperationsDia = OperacionDia.objects.all()
        for operationDay in listOperationsDia:
            operation_general.operaciones.add(operationDay)

        operations_day.delete()

        messages.success(request, 'Venta cerrada satisfactoriamente')
        return redirect('punto_venta')
    return redirect('login_user')


def punto_venta(request):
    products = Producto.objects.all()
    pedidos = Pedido.objects.all()
    history = Historial.objects.all()
    isClose = CerrarOperacion.objects.all().last()
    context = {'productos': products, 'pedidos': pedidos, 'cerrarOperation': isClose, 'history': history}
    return render(request, "control_panel/gestion_del_sitio/operaciones/punto_venta.html", context)


def carrito(request):
    pedidos = Pedido.objects.all()
    total_pagar = 0.0
    for pedido in pedidos:
        multi = pedido.cantidad_producto * pedido.producto.precio
        total_pagar += multi
    context = {'pedidos': pedidos, 'total_pagar': total_pagar}
    return render(request, "control_panel/gestion_del_sitio/operaciones/carrito.html", context)


def add_order(request, id_p):
    if request.user.is_authenticated:
        if request.method == "POST":
            producto_custom = Producto.objects.get(id=id_p)
            count_product = request.POST.get('count_product')
            c = Pedido.objects.create(producto=producto_custom, cantidad_producto=int(count_product))
            c.save()
            messages.success(request, 'Producto agregado al carrito')
            return redirect('punto_venta')
        context = {}
        return render(request, "control_panel/gestion_del_sitio/operaciones/punto_venta.html", context)
    return redirect('login_user')


def edit_order(request, id_o=None):
    if request.user.is_authenticated:
        pedido = Pedido.objects.get(id=id_o)
        if request.method == 'POST':
            count_product = request.POST.get('count_product')

            Pedido.objects.filter(id=id_o).update(cantidad_producto=count_product)

            messages.success(request, 'La cantidad de ' + pedido.producto.nombre_producto + ' fue modificada '
                                                                                            'satisfactoriamente')
            return redirect('carrito')
        context = {'pedido': pedido}
        return render(request, 'control_panel/gestion_del_sitio/productos/categorias_productos'
                               '/modificar_categoria_producto.html', context)
    return redirect('login_user')


def delete_order(request, id_o):
    if request.user.is_authenticated:
        pe = Pedido.objects.get(id=id_o)
        pe.delete()
        messages.success(request, 'Pedido eliminado satisfactoriamente')
        return redirect('carrito')
    return redirect('login_user')


def sales_order(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pedidos = Pedido.objects.all()
            total_pagar = 0.0
            for pedido in pedidos:
                multi = pedido.cantidad_producto * pedido.producto.precio
                total_pagar += multi
            payment_type = request.POST.get('payment_type')
            amount_client = request.POST.get('amount_client')
            if payment_type == 'cash' or payment_type == 'charge':
                value_return = float(amount_client) - total_pagar
                ope = Operacion.objects.create(
                    usuario=request.user,
                    tipo_pago=payment_type,
                    monto_total_a_pagar=total_pagar,
                    monto_pagado_cliente=amount_client,
                    monto_a_devolver=value_return,
                    fecha_operacion=datetime.now()
                )
                for order in pedidos:
                    history = Historial.objects.create(producto=order.producto,
                                                       cantidad_producto=order.cantidad_producto)
                    ope.pedidos.add(history)

                Pedido.objects.all().delete()

                return redirect(reverse('pago_confirmado', args=(ope.id,)))

            if payment_type == 'home_account':
                ope = Operacion.objects.create(
                    usuario=request.user,
                    tipo_pago=payment_type,
                    monto_total_a_pagar=total_pagar,
                    fecha_operacion=datetime.now()
                )

                for order in pedidos:
                    history = Historial.objects.create(producto=order.producto,
                                                       cantidad_producto=order.cantidad_producto)
                    ope.pedidos.add(history)

                Pedido.objects.all().delete()

                return redirect(reverse('pago_confirmado', args=(ope.id,)))

        context = {}
        return render(request, "control_panel/gestion_del_sitio/operaciones/carrito.html", context)
    return redirect('login_user')


def sales_order_transfer(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pedidos = Pedido.objects.all()
            total_pagar = 0.0
            for pedido in pedidos:
                multi = pedido.cantidad_producto * pedido.producto.precio
                total_pagar += multi
            payment_type = request.POST.get('payment_type')
            amount_client = request.POST.get('amount_client')
            transaction_code = request.POST.get('transaction_code')

            if payment_type == 'transfer':
                value_return = float(amount_client) - total_pagar
                ope = Operacion.objects.create(
                    usuario=request.user,
                    tipo_pago=payment_type,
                    monto_total_a_pagar=total_pagar,
                    monto_pagado_cliente=amount_client,
                    monto_a_devolver=value_return,
                    numero_de_transferencia=transaction_code,
                    fecha_operacion=datetime.now()
                )

                for order in pedidos:
                    history = Historial.objects.create(producto=order.producto,
                                                       cantidad_producto=order.cantidad_producto)
                    ope.pedidos.add(history)

                Pedido.objects.all().delete()

                return redirect(reverse('pago_confirmado', args=(ope.id,)))

        context = {}
        return render(request, "control_panel/gestion_del_sitio/operaciones/carrito.html", context)
    return redirect('login_user')


def pago_confirmado(request, id_op):
    user = request.user
    operation = get_object_or_404(Operacion, id=id_op)
    orders = Pedido.objects.all()
    if request.method == "POST":
        count_tip = request.POST.get('count_tip')
        Operacion.objects.filter(id=id_op).update(propina_del_cliente=float(count_tip))
        messages.success(request, 'Propina registrada satisfactoriamente')
        return redirect(reverse('pago_confirmado', args=(id_op,)))

    context = {
        'orders': orders,
        'operation': operation,
        'user': user
    }
    return render(request, "control_panel/gestion_del_sitio/operaciones/pago_confirmado.html", context)


def detalles_de_operation(request, id_op):
    operation = get_object_or_404(Operacion, id=id_op)
    context = {
        'operation': operation
    }
    return render(request, "control_panel/gestion_del_sitio/operaciones/detalles_de_operacion.html", context)


def factura_general(request, id_opg, id_op):
    operationGeneral = get_object_or_404(OperacionGeneral, id=id_opg)
    operation = get_object_or_404(OperacionDia, id=id_op)
    context = {
        'operationGeneral': operationGeneral,
        'operation': operation
    }
    return render(request, "control_panel/gestion_del_sitio/operaciones/detalles_factura.html", context)


def factura_resumen(request, id_op):
    operation = get_object_or_404(Operacion, id=id_op)
    context = {'operation': operation}
    return render(request, "control_panel/gestion_del_sitio/operaciones/resumen_venta.html", context)


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
                return redirect('insertar_usuario')
            elif password1 != password2:
                messages.warning(request,
                                 'Las contraseñas no coinciden, por favor escriba correctamente la contraseña')
                return redirect('insertar_usuario')
            else:
                if rol_de == 'dependiente':
                    User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        username=user_name,
                        is_dependiente=True,
                        is_moderador=False,
                        is_administrador=False,
                        sexo=genero
                    )
                elif rol_de == 'moderador':
                    User.objects.create_user(
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
                else:
                    User.objects.create_user(
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
            messages.success(request, 'Usuario registrado satisfactoriamente')
            return redirect('usuarios')
        context = {}
        return render(request, 'control_panel/gestion_de_usuarios/insertar_usuarios.html', context)
    return redirect('login_user')


def editar_usuario(request, id_user=None):
    if request.user.is_authenticated:
        user_custom = User.objects.get(id=id_user)
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
                if rol_de == 'dependiente':
                    User.objects.filter(id=id_user).update(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        username=user_name,
                        is_dependiente=True,
                        is_moderador=False,
                        is_administrador=False,
                        sexo=genero
                    )
                elif rol_de == 'moderador':
                    User.objects.filter(id=id_user).update(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        username=user_name,
                        is_dependiente=False,
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
                        is_dependiente=False,
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
