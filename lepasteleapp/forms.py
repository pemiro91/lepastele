import datetime

from django import forms

from lepasteleapp.models import Producto


class PiezaForm(forms.ModelForm):
    class Meta:
        model = Pieza
        fields = ('nombre_pieza', 'descripcion', 'categoria_pieza', 'precio', 'numero_referencia', 'url_video',
                  'imagen_principal')

        labels = {
            "nombre_pieza": "Nombre de la pieza",
            "descripcion": "Descripcion",
            "categoria_pieza": "Categoria de la pieza",
            "precio": "Precio",
            "numero_referencia": "Número de referencia",
            "url_video": "URL de Video",
            "imagen_principal": "Imagen principal",

        }
        widgets = {
            'nombre_pieza': forms.TextInput(
                attrs={'class': 'form-control text', 'placeholder': 'Escriba el nombre de la '
                                                                    'pieza', }),

            'descripcion': forms.Textarea(
                attrs={'class': 'form-control textarea', 'rows': 2, 'placeholder': 'Escriba la '
                                                                                   'descripción de la '
                                                                                   'pieza', }),
            'categoria_pieza': forms.Select(attrs={'class': 'select form-control', 'label': 'Seleccione '
                                                                                            'la '
                                                                                            'categoría', }),
            'precio': forms.TextInput(
                attrs={'class': 'form-control number ', 'placeholder': 'Escriba el precio de la pieza', }),
            'numero_referencia': forms.TextInput(
                attrs={'class': 'form-control number', 'placeholder': 'Escriba el número de referencia', }),
            'url_video': forms.URLInput(
                attrs={'class': 'form-control ', 'placeholder': 'Escriba la url de video', }),
            # 'imagen_principal': forms.FileInput(
            #     attrs={'class': 'form-control image', 'placeholder': 'Seleccione el archivo', }),

        }
