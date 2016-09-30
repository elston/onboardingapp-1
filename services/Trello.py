from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

import trolly

from team.models import Team, Service, TeamUser
from team.common import update_error_log
from .common import (
    check_service_instance, encrypt_data, decrypt_data, get_additional_info
)

TRELLO_ERRORS = {
    401: 'Token is incorrect. Please check again!',
    502: 'Team Short Name is incorrect. Please check again!',
}


class Trello:
    def get_form(self):
        return TrelloForm(initial={'name': 'Trello'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = TrelloForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            API_KEY = form.cleaned_data['key']
            TOKEN = form.cleaned_data['token']
            team_name = form.cleaned_data['team_name']

            team_id = self.check(form, API_KEY, TOKEN, team_name)

            if team_id:
                instance = check_service_instance(
                    team, s_name, TOKEN, API_KEY, team_name, team_id
                )

                if not instance:
                    service = self.create(s_name, API_KEY, TOKEN,
                                          team_name, team_id)
                    team.service.add(service)
                    team.save()

                    self.add_member_group(team, service)

                    return JsonResponse({'emails_list': []}, status=200)

                else:
                    form.errors['err'] = 'Second instance of service'

        return JsonResponse(form.errors, status=400)

    def check(self, form, API_KEY, TOKEN, team_name):
        try:
            client = trolly.client.Client(API_KEY, TOKEN)

            team_id = None
            for organisation in client.get_organisations():
                if organisation.name == team_name:
                    team_id = organisation.id
                    return team_id
                else:
                    form.errors['err'] = TRELLO_ERRORS[502]

        except Exception, e:
            if e.status == 401 or e.status == 502:
                form.errors['err'] = TRELLO_ERRORS[e.status]
            else:
                form.errors['err'] = str(e.status) + ": " + e.message

        return None

    def create(self, s_name, API_KEY, TOKEN, team_name, team_id):
        service = Service()
        service.name = s_name
        service.token = encrypt_data(TOKEN)
        service.org_name = API_KEY
        service.team_name = team_name
        service.team_id = team_id
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        client = trolly.client.Client(
            service.org_name, decrypt_data(service.token)
        )
        organisation = client.get_organisation(service.team_id)
        member_id = get_additional_info(teamuser, team, service)

        try:
            if member_id:
                organisation.add_member_by_id(member_id)
            else:
                organisation.add_member(teamuser.email, teamuser.email)
        except Exception as e:
            update_error_log(teamuser, team, service, e)

    def delete_membership_individual(self, email, service, **kwargs):
        team = kwargs['team']
        teamuser = get_object_or_404(TeamUser, email=email)
        member_id = get_additional_info(teamuser, team, service)

        client = trolly.client.Client(
            service.org_name, decrypt_data(service.token)
        )
        organisation = client.get_organisation(service.team_id)
        user_id = self.get_user_id_with_email(email, organisation)

        if member_id:
            organisation.remove_member(member_id)
        elif user_id:
            organisation.remove_member(user_id)

    def get_user_id_with_email(self, email, organisation):
        for member in organisation.get_members():
            if member.get_member_information()['email'] == email:
                return member.get_member_information()['id']
        return False

    def get_members_email(self, service, **kwargs):
        return []


class TrelloForm(forms.Form):
    key = forms.CharField(
        widget=forms.TextInput(attrs={
            'required': True, 'placeholder': 'Key',
            'oninput': 'javascript:key_input(); return false;'}),
        help_text='You can get your key <a href="https://trello.com/app-key" target="_blank">here</a>')
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Token'}),
        help_text='Aftering entering your key, <a href="" target="_blank" id="a_token_link">Click Here</a> to get your token.')
    team_name = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Team Short Name'}))
    name = forms.CharField(widget=forms.HiddenInput())
