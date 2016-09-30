import os
import base64
import json
import urllib
import requests

from django import forms
from django.conf import settings
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.core.urlresolvers import reverse_lazy

from team.models import Service
from team.common import update_error_log
from .common import encrypt_data, decrypt_data


class Dropbox:
    def get_form(self):
        return DropboxForm(initial={'name': 'Dropbox'})

    def Process(self, request, s_name, t_id):
        # form = DropboxForm(request.POST)
        request.session['t_id'] = t_id

        state = base64.urlsafe_b64encode(os.urandom(18))
        request.session['state'] = state
        redirect_uri = 'http://127.0.0.1:8000/service/Dropbox/auth-finish'
        # return redirect(
        #     'https://www.dropbox.com/1/oauth2/authorize?%s' %
        #     urllib.urlencode({
        #         'client_id': settings.DROPBOX_APP_KEY,
        #         'redirect_uri': redirect_uri,
        #         'response_type': 'code',
        #         'state': state
        #     })
        # )

        url = 'https://www.dropbox.com/1/oauth2/authorize?%s' % \
              urllib.urlencode({
                  'client_id': settings.DROPBOX_APP_KEY,
                  'redirect_uri': redirect_uri,
                  'response_type': 'code',
                  'state': state
              })

        return JsonResponse({'redirect': True, 'url': url}, status=200)

    def create(self, s_name, token, team_name, team_id):
        service = Service()
        service.name = s_name
        service.token = encrypt_data(token)
        service.team_name = team_name
        service.team_id = team_id
        service.save()

        return service

    def auth_finish(self, request, s_name, team):
        if request.GET.get('state') != request.session.pop('state', ''):
            raise Http404

        if request.GET.get('error'):
            # print request.GET.get('error_description')
            return redirect(reverse_lazy('team_info', kwargs={'id': team.pk}))

        redirect_uri = \
            'http://127.0.0.1:8000/add_service_real/Dropbox/auth-finish'
        data = requests.post(
            'https://api.dropbox.com/1/oauth2/token',
            data={
                'code': request.GET.get('code'),
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            },
            auth=(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET)
        ).json()

        token = data['access_token']

        info = requests.post(
            'https://api.dropbox.com/1/team/get_info',
            data=json.dumps({}),
            headers={
                'Content-Type': "application/json; charset=utf-8",
                'Authorization': 'Bearer %s' % token
            }).json()

        team_name = info['name']
        team_id = info['team_id']

        instance = team.service.filter(
            name=s_name, team_name=team_name, team_id=team_id)

        if not instance:
            service = self.create(s_name, token, team_name, team_id)
            team.service.add(service)
            team.save()

            self.add_member_group(team, service)

        return redirect(reverse_lazy('team_info', kwargs={'id': team.pk}))

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        data = requests.post(
            'https://api.dropbox.com/1/team/members/add',
            data=json.dumps({
                "member_email": teamuser.email,
                "member_given_name": teamuser.username,
                "send_welcome_email": True
            }),
            headers={
                'Content-Type': "application/json; charset=utf-8",
                'Authorization': 'Bearer %s' % decrypt_data(service.token)
            })

        if data.status_code != 200:
            data = data.json()
            try:
                texterror = data['error_description']
            except KeyError:
                texterror = data['error']

            update_error_log(teamuser, team, service, texterror)

    def delete_membership_individual(self, email, service, **kwargs):
        member_id = self.get_member_id_with_email(email, service)

        if member_id:
            requests.post(
                'https://api.dropbox.com/1/team/members/remove',
                data=json.dumps({'member_id': member_id}),
                headers={
                    'Content-Type': "application/json; charset=utf-8",
                    'Authorization': 'Bearer %s' % decrypt_data(service.token)
                })

    def get_member_id_with_email(self, email, service):
        member_id = None
        data = requests.post(
            'https://api.dropbox.com/1/team/members/get_info',
            data=json.dumps({'email': email}),
            headers={
                'Content-Type': "application/json; charset=utf-8",
                'Authorization': 'Bearer %s' % decrypt_data(service.token)
            })

        if data.status_code == 200:
            data = data.json()
            member_id = data['profile']['member_id']

        return member_id

    def get_members_list(self, service):
        members_list = []
        data = requests.post(
            'https://api.dropbox.com/1/team/members/list',
            data=json.dumps({}),
            headers={
                'Content-Type': "application/json; charset=utf-8",
                'Authorization': 'Bearer %s' % decrypt_data(service.token)
            })

        if data.status_code == 200:
            data = data.json()
            members_list = data['members']

        return members_list

    def get_emails_from_members_list(self, service, members_list):
        emails_list = []
        for member in members_list:
            emails_list.append(member['profile']['email'])

        return emails_list

    def get_members_email(self, service, **kwargs):
        members_list = self.get_members_list(service)
        emails_list_raw = self.get_emails_from_members_list(
            service, members_list)
        return emails_list_raw


class DropboxForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput())
