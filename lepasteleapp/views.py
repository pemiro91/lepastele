from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from datetime import datetime, date, timedelta
from django.db.models import Q, Count, Sum

from lepasteleapp.models import (User, Producto, Pedido, Operacion, FacturaFinal, Gastos, GastosGeneral,
                                 Categoria_Producto, Historial, CerrarOperacion, OperacionGeneral, OperacionDia)
from django.db import transaction
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.query import QuerySet
from django.utils import timezone
import pytz


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


class ProductCant:
    def __init__(self, id, nombre, categoria, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.cantidad = cantidad
        self.precio = precio


def panel_home(request):
    if request.user.is_authenticated:
        operaciones_generales = OperacionGeneral.objects.all()
        count_operaciones_generales_cash = OperacionDia.objects.filter(tipo_pago='cash').count()
        count_operaciones_generales_transfermovil = OperacionDia.objects.filter(tipo_pago='transfer').count()
        total_operaciones = 0
        monto_total = 0.0
        propina_total = 0.0
        for opg in operaciones_generales:
            total_operaciones += opg.operaciones.count()
            monto_total += opg.monto_total_dia
            propina_total += opg.propina_total_dia
        users = User.objects.filter(is_superuser=False).all()
        products = Producto.objects.all()
        isClose = CerrarOperacion.objects.filter(type_closed='caja').last()
        isCloseGeneral = CerrarOperacion.objects.filter(type_closed='general').last()

        operacionesDia = Operacion.objects.filter(usuario=request.user).order_by('-id')[:7]
        timezone.now()
        cantProduct = []
        for prod in products:
            listHistory = Historial.objects.filter(fecha__day=datetime.now().day).filter(producto=prod) \
                .aggregate(total=Sum('cantidad_producto'))
            prodCant = ProductCant(prod.id, prod.nombre_producto,
                                   prod.categoria_producto, listHistory['total'], prod.precio)
            cantProduct.append(prodCant)

        context = {'products': products, 'total_operaciones': total_operaciones,
                   'usuarios': users, 'monto_total': monto_total, 'cerrarOperation': isClose,
                   'countCash': count_operaciones_generales_cash,
                   'isCloseGeneral': isCloseGeneral, 'countTransfer': count_operaciones_generales_transfermovil,
                   'propina_total': propina_total, 'operacionesDia': operacionesDia, 'cantProduct': cantProduct}
        return render(request, "control_panel/index.html", context)
    return redirect('login_user')


#
# -----------------CRDU Categorias de productos---------------------------#
def categorias_productos(request):
    if request.user.is_authenticated:
        categorias_products = Categoria_Producto.objects.all()
        context = {'categorias_productos': categorias_products}
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


# -----------------CRUD Productos----------------------------------------#
def productos(request):
    products = Producto.objects.all()
    context = {'productos': products}
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
    operationsTotal = Operacion.objects.exclude(tipo_pago='home_account')
    total_dia = 0.0
    propina_dia = 0.0
    for ope in operationsTotal:
        print(ope.monto_total_a_pagar)
        total_dia += ope.monto_total_a_pagar
        if ope.propina_del_cliente is None:
            propina_dia += 0.0
        else:
            propina_dia += ope.propina_del_cliente
    isCloseCaja = CerrarOperacion.objects.filter(type_closed='caja', is_closed=True).last()
    isClose = CerrarOperacion.objects.filter(type_closed='general').last()
    context = {'operaciones': operations, 'total_dia': total_dia, 'propina_dia': propina_dia,
               'cerrarOperation': isClose, 'isCloseCaja': isCloseCaja}
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
    # operationsGeneral = OperacionDia.objects.all()
    total_venta_general = 0.0
    propina_general = 0.0
    listCantidadVentas = []
    listTemp = QuerySet
    for o in operationsGeneral:
        cantidadVentas = OperacionDia.objects.filter(fecha_operacion__year=o.fecha_operacion.year,
                                                     fecha_operacion__month=o.fecha_operacion.month,
                                                     fecha_operacion__day=o.fecha_operacion.day
                                                     ).count()

        listTemp = OperacionDia.objects.filter(fecha_operacion__year=o.fecha_operacion.year,
                                               fecha_operacion__month=o.fecha_operacion.month,
                                               fecha_operacion__day=o.fecha_operacion.day).filter(
            tipo_pago='home_account')

        obVenta = Ventas(o.id, o.monto_total_dia, o.propina_total_dia, cantidadVentas, o.fecha_operacion)
        listCantidadVentas.append(obVenta)

    for operat in operationsGeneral:
        total_venta_general += operat.monto_total_dia
        if operat.propina_total_dia is None:
            propina_general += 0.0
        else:
            propina_general += operat.propina_total_dia

    cuentaCasaTotal = 0.0
    for cuenta in listTemp:
        cuentaCasaTotal += cuenta.monto_total_a_pagar

    totalVentaGeneral = total_venta_general - cuentaCasaTotal
    context = {'operationsGeneral': listCantidadVentas,
               'total_venta_general': totalVentaGeneral, 'propina_general': propina_general}
    return render(request, "control_panel/gestion_del_sitio/operaciones/ventas_general.html", context)


def detalles_de_operation_general(request, id_op):
    operation = get_object_or_404(OperacionGeneral, id=id_op)
    total_venta_general = operation.monto_total_dia
    propina_general = operation.propina_total_dia

    totalVentas = OperacionDia.objects.filter(fecha_operacion__year=operation.fecha_operacion.year,
                                              fecha_operacion__month=operation.fecha_operacion.month,
                                              fecha_operacion__day=operation.fecha_operacion.day)

    totalVentasCash = OperacionDia.objects.filter(fecha_operacion__year=operation.fecha_operacion.year,
                                                  fecha_operacion__month=operation.fecha_operacion.month,
                                                  fecha_operacion__day=operation.fecha_operacion.day).filter(
        tipo_pago='cash')

    totalVentasTransfer = OperacionDia.objects.filter(fecha_operacion__year=operation.fecha_operacion.year,
                                                      fecha_operacion__month=operation.fecha_operacion.month,
                                                      fecha_operacion__day=operation.fecha_operacion.day).filter(
        tipo_pago='transfer')

    listTemp = OperacionDia.objects.filter(fecha_operacion__year=operation.fecha_operacion.year,
                                           fecha_operacion__month=operation.fecha_operacion.month,
                                           fecha_operacion__day=operation.fecha_operacion.day).filter(
        tipo_pago='home_account')

    cuentaCasaTotal = 0.0
    cashTotal = 0.0
    transferTotal = 0.0
    for cash in totalVentasCash:
        cashTotal += cash.monto_total_a_pagar
    for transfer in totalVentasTransfer:
        transferTotal += transfer.monto_total_a_pagar
    for cuenta in listTemp:
        cuentaCasaTotal += cuenta.monto_total_a_pagar

    totalVentaGeneral = total_venta_general - cuentaCasaTotal

    context = {
        'operation': operation,
        'total_venta_general': totalVentaGeneral,
        'propina_general': propina_general,
        'totalVentas': totalVentas,
        'cashTotal': cashTotal,
        'transferTotal': transferTotal
    }
    return render(request, "control_panel/gestion_del_sitio/operaciones/detalles_operacion_general.html", context)


def abrir_caja(request):
    if request.user.is_authenticated:
        isClose = CerrarOperacion.objects.filter(type_closed='caja').last()
        if not isClose:
            CerrarOperacion.objects.create(is_closed=False, type_closed='caja',
                                           usuario=request.user, fecha_cierre=datetime.now())
        else:
            CerrarOperacion.objects.filter(id=isClose.id).update(is_closed=False)
        messages.success(request, 'Venta abierta satisfactoriamente')
        return redirect('punto_venta_categoria')
    return redirect('login_user')


def cerrar_caja(request):
    if request.user.is_authenticated:
        CerrarOperacion.objects.create(is_closed=True, type_closed='caja',
                                       usuario=request.user, fecha_cierre=datetime.now())
        messages.success(request, 'Caja cerrada satisfactoriamente')
        return redirect('operaciones')
    return redirect('login_user')


def cerrar_venta(request):
    if request.user.is_authenticated:
        CerrarOperacion.objects.create(is_closed=True, type_closed='general',
                                       usuario=request.user, fecha_cierre=datetime.now())
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
                                                      cantidad_producto=itemOpero.cantidad_producto,
                                                      fecha=datetime.now())
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

        gastos = Gastos.objects.filter(fecha_gasto__year=datetime.now().year,
                                       fecha_gasto__month=datetime.now().month,
                                       fecha_gasto__day=datetime.now().day)
        gasto_dia = 0.0
        for gasto in gastos:
            gasto_dia += gasto.monto_gasto

        print(gasto_dia)

        GastosGeneral.objects.create(monto_gasto_general=gasto_dia, fecha_gasto_general=datetime.now())

        for operationDay in listOperationsDia:
            operation_general.operaciones.add(operationDay)

        operations_day.delete()

        messages.success(request, 'Venta cerrada satisfactoriamente')
        return redirect('operaciones_general')
    return redirect('login_user')


class CategoryProduct:
    def __init__(self, id, nombre_categoria, descripcion_category, countProduct):
        self.id = id
        self.nombre_categoria = nombre_categoria
        self.descripcion_category = descripcion_category
        self.countProduct = countProduct


def punto_venta_categoria(request):
    if request.user.is_authenticated:
        categorias_products = Categoria_Producto.objects.all()
        products = Producto.objects.all()
        pedidos = Pedido.objects.all()
        history = Historial.objects.all()
        isClose = CerrarOperacion.objects.filter(type_closed='caja').last()

        lisCountP = []
        for catP in categorias_products:
            prodCount = Producto.objects.filter(categoria_producto=catP).all().count()
            categoryProduct = CategoryProduct(catP.id, catP.nombre_categoria, catP.descripcion, prodCount)
            lisCountP.append(categoryProduct)

        context = {'categorias_productos': lisCountP, 'productos': products,
                   'pedidos': pedidos, 'cerrarOperation': isClose, 'history': history}
        return render(request, "control_panel/gestion_del_sitio/operaciones/punto_venta_categorias.html", context)
    return redirect('login_user')


def add_spending(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            description_amount = request.POST.get('description_amount')
            gasto_amount = request.POST.get('gasto_amount')
            c = Gastos.objects.create(usuario=request.user, descripcion_gasto=description_amount,
                                      monto_gasto=gasto_amount, fecha_gasto=datetime.now())
            c.save()
            messages.success(request, 'Gasto registrado satisfactoriamente')
            return redirect('punto_venta_categoria')
        context = {}
        return render(request, "control_panel/gestion_del_sitio/operaciones/punto_venta.html", context)
    return redirect('login_user')


def gastos_dia(request):
    if request.user.is_authenticated:
        gastos = Gastos.objects.filter(fecha_gasto__year=datetime.now().year,
                                       fecha_gasto__month=datetime.now().month,
                                       fecha_gasto__day=datetime.now().day)
        totalGastosDia = 0.0
        for gasto in gastos:
            totalGastosDia += gasto.monto_gasto
        context = {'gastos': gastos, 'totalGastosDia': totalGastosDia}
        return render(request, "control_panel/gestion_del_sitio/operaciones/gastos/gastos_dia.html", context)
    return redirect('login_user')


def gastos_general(request):
    if request.user.is_authenticated:
        gastos = GastosGeneral.objects.all()
        totalGastosGeneral = 0.0
        for gasto in gastos:
            totalGastosGeneral += gasto.monto_gasto_general
        context = {'gastos': gastos, 'totalGastosGeneral': totalGastosGeneral}
        return render(request, "control_panel/gestion_del_sitio/operaciones/gastos/gastos_general.html", context)
    return redirect('login_user')


def gastos_dia_general(request, id_gg):
    if request.user.is_authenticated:
        gastoGeneral = get_object_or_404(GastosGeneral, id=id_gg)
        gastos = Gastos.objects.filter(fecha_gasto__year=gastoGeneral.fecha_gasto_general.year,
                                       fecha_gasto__month=gastoGeneral.fecha_gasto_general.month,
                                       fecha_gasto__day=gastoGeneral.fecha_gasto_general.day)
        totalGastosDia = 0.0
        for gasto in gastos:
            totalGastosDia += gasto.monto_gasto
        context = {'gastos': gastos, 'totalGastosDia': totalGastosDia, 'id_gg': id_gg}
        return render(request, "control_panel/gestion_del_sitio/operaciones/gastos/gastos_dia.html", context)
    return redirect('login_user')


def punto_venta(request, id_cat):
    if request.user.is_authenticated:
        category = get_object_or_404(Categoria_Producto, id=id_cat)
        products = Producto.objects.filter(categoria_producto=id_cat)
        pedidos = Pedido.objects.all()
        history = Historial.objects.all()
        isClose = CerrarOperacion.objects.filter(type_closed='caja').last()
        context = {'productos': products, 'pedidos': pedidos, 'cerrarOperation': isClose, 'history': history,
                   'category': category}
        return render(request, "control_panel/gestion_del_sitio/operaciones/punto_venta.html", context)
    return redirect('login_user')


def carrito(request):
    pedidos = Pedido.objects.all()
    total_pagar = 0.0
    for pedido in pedidos:
        multi = pedido.cantidad_producto * pedido.producto.precio
        total_pagar += multi
    context = {'pedidos': pedidos, 'total_pagar': total_pagar}
    return render(request, "control_panel/gestion_del_sitio/operaciones/carrito.html", context)


def add_order(request, id_cat, id_p):
    if request.user.is_authenticated:
        if request.method == "POST":
            producto_custom = Producto.objects.get(id=id_p)
            count_product = request.POST.get('count_product')
            c = Pedido.objects.create(producto=producto_custom, cantidad_producto=int(count_product),
                                      fecha=datetime.now())
            c.save()
            messages.success(request, 'Producto agregado al carrito')
            print(id_cat)
            return redirect(reverse('punto_venta', args=(id_cat,)))
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
                                                       cantidad_producto=order.cantidad_producto,
                                                       fecha=order.fecha)
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
                                                       cantidad_producto=order.cantidad_producto,
                                                       fecha=order.fecha)
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
                                                       cantidad_producto=order.cantidad_producto,
                                                       fecha=order.fecha)
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
