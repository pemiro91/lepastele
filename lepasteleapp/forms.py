import datetime

from django import forms

from lepasteleapp.models import Producto, Operacion


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('nombre_producto', 'descripcion', 'categoria_producto', 'precio')

        labels = {
            "nombre_producto": "Nombre del producto",
            "descripcion": "Descripcion",
            "categoria_producto": "Categoria de producto",
            "precio": "Precio"}

        widgets = {
            'nombre_producto': forms.TextInput(
                attrs={'class': 'form-control text', 'placeholder': 'Escriba el nombre del '
                                                                    'producto', }),

            'descripcion': forms.Textarea(
                attrs={'class': 'form-control textarea', 'rows': 2, 'placeholder': 'Escriba la '
                                                                                   'descripción del '
                                                                                   'producto', }),
            'categoria_producto': forms.Select(attrs={'class': 'select form-control', 'label': 'Seleccione '
                                                                                               'la '
                                                                                               'categoría', }),
            'precio': forms.TextInput(
                attrs={'class': 'form-control number ', 'placeholder': 'Escriba el precio de la pieza', })

        }


# class OperacionForm(forms.ModelForm):
#     class Meta:
#         model = Operacion
#         fields = ('pedidos', 'fecha_operacion', 'tipo_pago')
#
#         labels = {
#             "pedidos": "Pedido(s)",
#             "tipo_pago": "Tipo de pago",
#             "fecha_operacion": "Fecha"}
#
#         widgets = {
#             'nombre_producto': forms.TextInput(
#                 attrs={'class': 'form-control text', 'placeholder': 'Escriba el nombre del '
#                                                                     'producto', }),
#
#             'descripcion': forms.Textarea(
#                 attrs={'class': 'form-control textarea', 'rows': 2, 'placeholder': 'Escriba la '
#                                                                                    'descripción del '
#                                                                                    'producto', }),
#             'pedidos': forms.Select(attrs={'class': 'select multiple form-control ', 'label': 'Seleccione '
#                                                                                                'la '
#                                                                                                'categoría', }),
#             'precio': forms.TextInput(
#                 attrs={'class': 'form-control number ', 'placeholder': 'Escriba el precio de la pieza', })
#
#         }
