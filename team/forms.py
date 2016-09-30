from django import forms
from organization.models import Organization


class UserInviteForm(forms.Form):
    team = forms.CharField(widget=forms.HiddenInput())
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
        required=False
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
        required=False
    )
    user_email = forms.CharField(
        widget=forms.TextInput(
            attrs={'required': True, 'placeholder': 'User Email'}),
    )
    admin = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'styled', 'checked': True, 'id': 'checkbox2'}),
        label='Admin', required=False
    )


class CreateTeamForm1(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True, empty_label=None)
    team_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'required': True, 'placeholder': 'Team Name'}))
    team_description = forms.CharField(
        widget=forms.TextInput(
            attrs={'required': True, 'placeholder': 'Team Description'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CreateTeamForm1, self).__init__(*args, **kwargs)

        if user:
            self.fields['organization'].queryset = Organization.objects.filter(
                owner=user)


class CreateTeamForm2(forms.Form):
    organization = forms.CharField(
        widget=forms.TextInput(
            attrs={'required': True, 'placeholder': 'Company or orginization name'}))
    team_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'required': True, 'placeholder': 'Team Name'}))
    team_description = forms.CharField(
        widget=forms.TextInput(
            attrs={'required': True, 'placeholder': 'Team Description'}))
