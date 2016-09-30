import json
import requests

from django import forms
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service
from team.common import update_error_log, check_emails_list_for_team_members
from .common import check_service_instance, encrypt_data, decrypt_data

ASANA_ERRORS = {
    401: 'Token is not correct. Please check again!'
}


class Asana:
    def get_form(self):
        return AsanaForm(initial={'name': 'Asana'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = AsanaForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            workspace_id = self.check(form)

            if workspace_id:
                instance = check_service_instance(
                    team, s_name, form.cleaned_data['token'],
                    form.cleaned_data['workspace'], None, workspace_id
                )

                if not instance:
                    service = self.create(form, s_name, workspace_id)
                    team.service.add(service)
                    team.save()

                    self.add_member_group(team, service)

                    emails_list = check_emails_list_for_team_members(
                        self.get_members_email(service),
                        team.member.all()
                    )
                    return JsonResponse(
                        {'emails_list': emails_list}, status=200)

                else:
                    form.errors['err'] = 'Second instance of service'

        return JsonResponse(form.errors, status=400)

    def check(self, form):
        workspace_id = None
        url = 'https://app.asana.com/api/1.0/workspaces'
        header = {"Authorization": 'Bearer ' + form.cleaned_data['token']}
        res = requests.get(url, headers=header)

        if res.status_code != 200:
            form.errors['err'] = ASANA_ERRORS[res.status_code]
        else:
            res_json = res.json()
            for item in res_json['data']:
                if item['name'] == form.cleaned_data['workspace']:
                    workspace_id = item['id']
                    break

            if not workspace_id:
                err = 'There is no such workspace. Please check again!'
                form.errors['err'] = err

        return workspace_id

    def create(self, form, s_name, workspace_id):
        service = Service()
        service.name = s_name
        service.token = encrypt_data(form.cleaned_data['token'])
        service.org_name = form.cleaned_data['workspace']
        service.team_id = workspace_id
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        url = 'https://app.asana.com/api/1.0/workspaces/%s/addUser' % \
              service.team_id
        header = {"Authorization": 'Bearer ' + decrypt_data(service.token)}
        data = {'data': {'user': teamuser.email}}
        res = requests.post(url, data=json.dumps(data), headers=header)

        if res.status_code != requests.codes.ok:
            res_json = res.json()
            update_error_log(
                teamuser, team, service, res_json['errors'][0]['message'])

    def delete_membership_individual(self, email, service, **kwargs):
        url = 'https://app.asana.com/api/1.0/workspaces/%s/removeUser' % \
              service.team_id
        header = {"Authorization": 'Bearer ' + decrypt_data(service.token)}
        data = {'data': {'user': email}}
        requests.post(url, data=json.dumps(data), headers=header)

    def get_members_list(self, service):
        members_list = []

        url = 'https://app.asana.com/api/1.0/workspaces/%s/users' % \
              service.team_id
        header = {"Authorization": 'Bearer ' + decrypt_data(service.token)}
        res = requests.get(url, headers=header)

        res_json = res.json()
        for item in res_json['data']:
            members_list.append(item['id'])

        return members_list

    def get_emails_from_members_list(self, members_list, service):
        emails_list = []

        header = {"Authorization": 'Bearer ' + decrypt_data(service.token)}
        for member in members_list:
            url = 'https://app.asana.com/api/1.0/users/%s' % member
            res = requests.get(url, headers=header)
            if res.status_code == 200:
                res_json = res.json()
                emails_list.append(res_json['data']['email'])

        return emails_list

    def get_members_email(self, service, **kwargs):
        members_list = self.get_members_list(service)
        emails_list_raw = self.get_emails_from_members_list(
            members_list, service)
        return emails_list_raw


class AsanaForm(forms.Form):
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Token'}),
        help_text='You can get your token in "My Profile Settings" -> "Apps" -> "Manage Developer Apps" -> "Create New Personal Access Token"')
    workspace = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Workspace'}))
    name = forms.CharField(widget=forms.HiddenInput())
