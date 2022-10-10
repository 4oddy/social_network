from django import forms

from .models import Conservation


class CreateConservationForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        label='Участники',
        queryset=None,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Conservation
        fields = ('name', 'members')
