from django import forms

from controls.models import LightShow, LightShowStep



class LightShowForm(forms.ModelForm):
    class Meta:
        model = LightShow
        fields = (
            'name',
        )

class LightShowStepForm(forms.ModelForm):
    class Meta:
        model = LightShowStep
        fields = (
            'show', 'light', 'red', 'green', 'blue', 'order',
        )