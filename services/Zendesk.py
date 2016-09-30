import json
import requests

from django import forms
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service
from team.common import update_error_log, check_emails_list_for_team_members
from .common import check_service_instance, encrypt_data, decrypt_data


class Zendesk:
    def get_form(self):
        return ZendeskForm(initial={'name': 'Zendesk'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = ZendeskForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            response = self.check(form, team)
            if response:
                instance = check_service_instance(
                    team, s_name,
                    form.cleaned_data['token'],
                    form.cleaned_data['subdomain']
                )

                if not instance:
                    service = self.create(form, s_name)
                    team.service.add(service)
                    team.save()

                    self.add_member_group(team, service)

                    emails_list = check_emails_list_for_team_members(
                        self.get_members_email(service, team=team),
                        team.member.all()
                    )
                    return JsonResponse(
                        {'emails_list': emails_list}, status=200)

                else:
                    form.errors['err'] = 'Second instance of service'

        return JsonResponse(form.errors, status=400)

    def check(self, form, team):
        user = team.owner.email + '/token'
        url = 'https://%s.zendesk.com/api/v2/account/settings.json' % \
              form.cleaned_data['subdomain']

        response = requests.get(url, auth=(user, form.cleaned_data['token']))

        if response.status_code != 200:
            res_json = response.json()
            if type(res_json['error']) is dict:
                err = res_json['error']['title'] + ": " + \
                      res_json['error']['message']
            else:
                err = res_json['error']

            form.errors['err'] = err
            return False

        return True

    def create(self, form, s_name):
        service = Service()
        service.name = s_name
        service.token = encrypt_data(form.cleaned_data['token'])
        service.org_name = form.cleaned_data['subdomain']
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        user = team.owner.email + '/token'
        url = 'https://%s.zendesk.com/api/v2/users.json' % service.org_name
        header = {"Content-Type": 'application/json'}
        data = {
            'user': {
                'name': teamuser.username,
                'email': teamuser.email,
                'role': 'agent'
            }
        }

        response = requests.post(url, auth=(user, decrypt_data(service.token)),
                                 headers=header, data=json.dumps(data))

        if response.status_code != 201:
            update_error_log(teamuser, team, service, response.text)

    def delete_membership_individual(self, email, service, **kwargs):
        team = kwargs['team']
        member_id = self.get_member_id_with_email(email, team, service)

        if member_id:
            user = team.owner.email + '/token'
            url = 'https://%s.zendesk.com/api/v2/users/%s.json' % (
                service.org_name, member_id)
            requests.delete(url, auth=(user, decrypt_data(service.token)))

    def get_members_list(self, team, service):
        members_list = []
        user = team.owner.email + '/token'
        url = 'https://%s.zendesk.com/api/v2/users.json' % service.org_name
        response = requests.get(url, auth=(user, decrypt_data(service.token)))

        if response.status_code == 200:
            res_json = response.json()
            members_list = res_json['users']

        return members_list

    def get_member_id_with_email(self, email, team, service):
        member_id = []

        members_list = self.get_members_list(team, service)
        for item in members_list:
            if item['email'] == email:
                member_id = item['id']
                break

        return member_id

    def get_emails_from_members_list(self, members_list):
        emails_list = []
        for member in members_list:
            emails_list.append(member['email'])

        return emails_list

    def get_members_email(self, service, **kwargs):
        team = kwargs['team']
        members_list = self.get_members_list(team, service)
        emails_list_raw = self.get_emails_from_members_list(members_list)

        return emails_list_raw


class ZendeskForm(forms.Form):
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Token'}))
    subdomain = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Subdomain'}))
    name = forms.CharField(widget=forms.HiddenInput())
