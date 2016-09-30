from django import forms
from .models import Organization


class OrganizationCreateForm(forms.ModelForm):
    name = forms.CharField(
        widget=(forms.TextInput(attrs={'placeholder': 'Organization Name'})))
    description = forms.CharField(
        widget=(forms.Textarea(attrs={'placeholder': 'Description'})),
        required=False
    )

    class Meta:
        model = Organization
        exclude = ('owner', 'team')
