from django import forms
import numpy as np
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in np.arange(0, 20.5, 0.5)]
class CartAddProductForm(forms.Form):
    quantite = forms.TypedChoiceField(
                                choices=PRODUCT_QUANTITY_CHOICES,
                                coerce=int)
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)