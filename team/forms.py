from django import forms
from organization.models import Organization
from .models import TeamUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext, ugettext_lazy as _

class UserCreationForm(forms.ModelForm):
    # ...
    password1 = forms.CharField(label='Password', 
        widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', 
        widget=forms.PasswordInput)

    class Meta:
        model = TeamUser
        fields = ('email','username')

    def clean_password2(self):
        # ...
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # ..
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            "using <a href=\"../password/\">this form</a>."))

    class Meta:
        model = TeamUser
        fields = ('email', 'password', 'is_active', 'is_superuser')

    def clean_password(self):
        return self.initial["password"]



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
    # admin = forms.BooleanField(
    #     widget=forms.CheckboxInput(
    #         attrs={'class': 'styled', 'checked': True, 'id': 'checkbox2'}),
    #     label='Admin', required=False
    # )

 
class TeamEditForm(forms.Form):
    team = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Team name'}),
        required=True
    ) 
    description = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Team description'}),
        required=False
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

    is_member = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'styled', 'checked': True, 'id': 'id_is_member'}),
        label='Add to the team as a member', required=False
    )

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

    is_member = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'styled', 'checked': True, 'id': 'id_is_member'}),
        label='Add to the team as a member', required=False
    )    


class ChangeTeamOwnerForm(forms.Form):
    team = forms.CharField(widget=forms.HiddenInput())    
    owner = forms.ModelChoiceField(
        queryset=TeamUser.objects.all(),
        required=True, empty_label=None)

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super(ChangeTeamOwnerForm, self).__init__(*args, **kwargs)

        if team:
            self.fields['owner'].queryset = team.member.exclude(
                id=team.owner.id)