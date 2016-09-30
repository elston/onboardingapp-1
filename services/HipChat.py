import requests
import json

from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service, TeamUser
from team.common import update_error_log, check_emails_list_for_team_members
from .common import (
    check_service_instance, encrypt_data, decrypt_data, get_additional_info
)


class HipChat:
    def get_form(self):
        return HipChatForm(initial={'name': 'HipChat'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = HipChatForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            room = self.check(form)

            if room:
                instance = check_service_instance(
                    team, s_name,
                    form.cleaned_data['token'], room
                )

                if not instance:
                    service = self.create(form, s_name, room)
                    team.service.add(service)
                    team.save()

                    self.add_member_group(team, service)

                    emails_list = check_emails_list_for_team_members(
                        self.get_members_email(service), team.member.all()
                    )

                    return JsonResponse(
                        {'emails_list': emails_list}, status=200)

                else:
                    form.errors['err'] = 'Second instance of service'

        return JsonResponse(form.errors, status=400)

    def check(self, form):
        url = 'https://api.hipchat.com/v2/room'
        header = {
            'Authorization': 'Bearer ' + form.cleaned_data['token'],
            'Content-Type': 'application/json'
        }
        res = requests.get(url=url, headers=header)

        if res.status_code != requests.codes.ok:
            if res.status_code == 401:
                err = 'The Token is incorrect. Please check again!'
                form.errors['err'] = err
            else:
                res_json = res.json()
                form.errors['err'] = res_json['error']['message']
        else:
            res_json = res.json()
            room = None
            for item in res_json['items']:
                if item['name'] == form.cleaned_data['org_name']:
                    room = item['name']
                    return room

                if not room:
                    err = 'There is no such room. Please check again!'
                    form.errors['err'] = err

        return None

    def create(self, form, s_name, room):
        token = encrypt_data(form.cleaned_data['token'])
        service = Service()
        service.name = s_name
        service.token = token
        service.org_name = room
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        email = teamuser.email
        mention_name = get_additional_info(teamuser, team, service)

        if mention_name:
            url = 'https://api.hipchat.com/v2/room/%s/invite/%s' % (
                service.org_name, mention_name)
        else:
            url = 'https://api.hipchat.com/v2/room/%s/invite/%s' % (
                service.org_name, email)

        data = {}
        header = {
            'Authorization': 'Bearer ' + decrypt_data(service.token),
            'Content-Type': 'application/json'
        }
        res = requests.post(url=url, data=json.dumps(data), headers=header)

        if res.status_code != 204:
            update_error_log(teamuser, team, service, res.text)

    def delete_membership_individual(self, email, service, **kwargs):
        team = kwargs['team']
        teamuser = get_object_or_404(TeamUser, email=email)
        mention_name = get_additional_info(teamuser, team, service)

        if mention_name:
            url = 'https://api.hipchat.com/v2/room/%s/member/%s' % (
                service.org_name, mention_name)
        else:
            url = 'https://api.hipchat.com/v2/room/%s/member/%s' % (
                service.org_name, email)

        header = {'Authorization': 'Bearer ' + decrypt_data(service.token)}
        requests.delete(url=url, headers=header)

    def get_members_list(self, service):
        members_list = []
        url = 'https://api.hipchat.com/v2/room/%s/participant' % (
            service.org_name)
        header = {
            'Authorization': 'Bearer ' + decrypt_data(service.token),
            'Content-Type': 'application/json'
        }

        res = requests.get(url=url, headers=header)

        if res.status_code == requests.codes.ok:
            res_json = res.json()
            for item in res_json['items']:
                members_list.append(item['id'])

        return members_list

    def get_emails_from_members_list(self, service, members_list):
        emails_list = []
        header = {
            'Authorization': 'Bearer ' + decrypt_data(service.token),
            'Content-Type': 'application/json'
        }

        for member in members_list:
            url = 'https://api.hipchat.com/v2/user/%s' % member
            res = requests.get(url=url, headers=header)
            if res.status_code == requests.codes.ok:
                res_json = res.json()
                email = res_json['email']
                if email is not None:
                    emails_list.append(email)

        return emails_list

    def get_members_email(self, service, **kwargs):
        members = self.get_members_list(service)
        emails_raw = self.get_emails_from_members_list(service, members)

        return emails_raw


class HipChatForm(forms.Form):
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Token'}),
        help_text='You can get your token here: https://{ROOM_NAME}.hipchat.com/account/confirm_password?redirect_to=/account/api')
    org_name = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Room Name'}))
    name = forms.CharField(widget=forms.HiddenInput())
