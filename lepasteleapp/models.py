import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
# from tinymce import models
from django.template.defaultfilters import slugify

import uuid

# from ckeditor.fields import RichTextField

TIPO_PAGO = (
    ('En Efectivo', 'En_Efectivo'),
    ('Transferencia', 'Transferencia'),
    ('Por encargo', 'Por_Encargo'),
    ('Cuenta Casa', 'Cuenta_Casa')
)


def images_directory_path(instance, filename):
    return '/'.join(['images', str(instance.title), str(uuid.uuid4().hex + ".png")])


class User(AbstractUser):
    sexo = models.BooleanField(default=False)
    is_dependiente = models.BooleanField(default=True)
    is_moderador = models.BooleanField(default=True)
    is_administrador = models.BooleanField(default=False)


class Categoria_Producto(models.Model):
    nombre_categoria = models.CharField(max_length=50)
    descripcion_categoria = models.TextField(max_length=50, name='descripcion')

    # tipo_pieza = models.BooleanField(name='tipo_pieza')

    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):
    categoria_producto = models.ForeignKey(Categoria_Producto, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=100, name='nombre_producto')
    descripcion = models.CharField(max_length=100, name='descripcion')
    precio = models.FloatField(max_length=100, name='precio')

    # imagen_principal = models.ImageField(upload_to='pieza/', null=True, blank=True)

    def __str__(self):
        return self.nombre_producto


class Pedido(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, name='producto')
    cantidad_producto = models.IntegerField()

    def str(self):
        return str(self.producto)


class Operacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, name='usuario')
    pedidos = models.ManyToManyField(Pedido)
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO, name='tipo_pago')
    # Solo para efectivo, transferencia, encargo
    monto_total_a_pagar = models.FloatField(max_length=100)
    monto_pagado_cliente = models.FloatField(max_length=100)
    monto_a_devolver = models.FloatField(max_length=100)
    # Solo para transferencia
    numero_de_transferencia = models.CharField(max_length=100, blank=True, name='numero_de_transferencia')
    # Solo para efectivo, transferencia, encargo
    propina_del_cliente = models.FloatField(max_length=100)
    fecha_operacion = models.DateTimeField(datetime.datetime.now())

    def str(self):
        return str(self.pedidos)

# def get_image_filename(instance, filename):
#     nombre_pieza = instance.pieza.nombre_producto
#     slug = slugify(nombre_pieza)
#     return "productos_imagenes/%s-%s" % (slug, filename)

#
# class Imagenes(models.Model):
#     producto = models.ForeignKey(Producto, default=None, on_delete=models.CASCADE)
#     imagen = models.ImageField(upload_to=get_image_filename,
#                                verbose_name='imagen')
