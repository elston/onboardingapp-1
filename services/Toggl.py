import json
import requests

from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service
from team.common import update_error_log, check_emails_list_for_team_members
from .common import check_service_instance, encrypt_data, decrypt_data


class Toggl:
    def get_form(self):
        return TogglForm(initial={'name': 'Toggl'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = TogglForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            workspace_id = self.check(form)

            if workspace_id:
                instance = check_service_instance(
                    team, s_name,
                    form.cleaned_data['token'],
                    None, form.cleaned_data['workspace'],
                    workspace_id
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
        url = 'https://www.toggl.com/api/v8/me'
        res = requests.get(url,
                           auth=(form.cleaned_data['token'], 'api_token'))
        if res.status_code != 200:
            form.errors['err'] = 'Token is not correct. Please check again!'
        else:
            res_json = res.json()
            for item in res_json['data']['workspaces']:
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
        service.team_name = form.cleaned_data['workspace']
        service.team_id = workspace_id
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        url = 'https://www.toggl.com/api/v8/workspaces/%s/invite' % \
              service.team_id
        header = {"Content-Type": 'application/json'}
        data = {'emails': [teamuser.email]}

        res = requests.post(url,
                            auth=(decrypt_data(service.token), 'api_token'),
                            data=json.dumps(data), headers=header)

        res_json = res.json()
        if res_json['data'] is None:
            update_error_log(
                teamuser, team, service, res_json['notifications'])

    def delete_membership_individual(self, email, service, **kwargs):
        workspace_uid = self.get_workspace_uid_with_email(email, service)
        if workspace_uid:
            url = 'https://www.toggl.com/api/v8/workspace_users/%s' % \
                  workspace_uid
            requests.delete(url,
                            auth=(decrypt_data(service.token), 'api_token'))

    def get_workspace_uid_with_email(self, email, service):
        members_list = self.get_members_list(service)

        workspace_uid = None
        for member in members_list:
            if member['email'] == email:
                workspace_uid = member['id']
                break

        return workspace_uid

    def get_members_list(self, service):
        members_list = []
        url = 'https://www.toggl.com/api/v8/workspaces/%s/workspace_users' % \
              service.team_id
        res = requests.get(url,
                           auth=(decrypt_data(service.token), 'api_token'))

        if res.status_code == 200:
            res_json = res.json()
            members_list = res_json

        return members_list

    def get_emails_from_members_list(self, members_list):
        emails_list = []
        for member in members_list:
            emails_list.append(member['email'])

        return emails_list

    def get_members_email(self, service, **kwargs):
        members_list = self.get_members_list(service)
        emails_list_raw = self.get_emails_from_members_list(members_list)
        return emails_list_raw


class TogglForm(forms.Form):
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Token'}))
    workspace = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Workspace'}))
    name = forms.CharField(widget=forms.HiddenInput())
