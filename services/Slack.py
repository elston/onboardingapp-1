import requests

from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service
from team.common import update_error_log, check_emails_list_for_team_members
from .common import check_service_instance, encrypt_data, decrypt_data


class Slack:
    def get_form(self):
        return SlackForm(initial={'name': 'Slack'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = SlackForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            r_json = self.check(form)

            if r_json:
                org_name = r_json['team']['name']
                team_name = r_json['team']['domain']
                team_id = r_json['team']['id']

                instance = check_service_instance(
                    team, s_name, form.cleaned_data['team_token'],
                    org_name, team_name, team_id
                )

                if not instance:
                    service = self.create(form, s_name, org_name,
                                          team_name, team_id)
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
        token = form.cleaned_data['team_token']
        url = 'https://slack.com/api/auth.test?token=%s' % token
        res = requests.post(url=url)
        res_json = res.json()

        if res_json['ok'] is not True:
            err = 'Team Token is incorrect. Please check again!'
            form.errors['err'] = err
        else:
            url = 'https://slack.com/api/team.info?token=%s' % token
            r = requests.post(url=url)
            r_json = r.json()

            if r_json['ok'] is True:
                return r_json
            else:
                form.erros['err'] = r_json['error']

        return None

    def create(self, form, s_name, org_name, team_name, team_id):
        token = encrypt_data(form.cleaned_data['team_token'])
        service = Service()
        service.name = s_name
        service.token = token
        service.org_name = org_name
        service.team_name = team_name
        service.team_id = team_id
        service.save()

        return service

    def add_member_group(self, team, service):
        '''
        add team members to slack with their emails
        '''
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        email = teamuser.email

        url = 'https://%s.slack.com/api/users.admin.invite?token=%s&email=%s&set_active=true' % (
            service.team_name, decrypt_data(service.token), email)

        res = requests.post(url=url)

        res_json = res.json()
        if 'error' in res_json and res_json['error'] == 'already_in_team':
            deleted = self.get_member_status(email, service)
            if deleted:
                id = self.get_member_id_with_email(email, service)
                url = 'https://%s.slack.com/api/users.admin.setRegular?token=%s&user=%s' % (
                    service.team_name, decrypt_data(service.token), id)
                res = requests.post(url=url)

        if 'ok' in res_json and res_json['ok'] is not True:
            update_error_log(teamuser, team, service, res_json['error'])

    def get_member_status(self, email, service):
        deleted = False
        url = 'https://slack.com/api/users.list?token=%s' % (
            decrypt_data(service.token))
        res = requests.post(url=url)

        if res.status_code == requests.codes.ok:
            res_json = res.json()
            for item in res_json['members']:
                if 'email' in item['profile']:
                    if email == item['profile']['email']:
                        deleted = item['deleted']

        return deleted

    def get_member_id_with_email(self, email, service):
        id = None
        url = 'https://slack.com/api/users.list?token=%s' % (
            decrypt_data(service.token))
        res = requests.post(url=url)

        if res.status_code == requests.codes.ok:
            res_json = res.json()
            for item in res_json['members']:
                if 'email' in item['profile']:
                    if email == item['profile']['email']:
                        id = item['id']

        return id

    def delete_membership_individual(self, email, service, **kwargs):
        id = self.get_member_id_with_email(email, service)
        url = 'https://%s.slack.com/api/users.admin.setInactive?token=%s&user=%s' % (
            service.team_name, decrypt_data(service.token), id)
        requests.post(url=url)

    def get_members_email(self, service, **kwargs):
        emails = []

        url = 'https://slack.com/api/users.list?token=%s' % (
            decrypt_data(service.token))
        res = requests.post(url=url)

        if res.status_code == requests.codes.ok:
            res_json = res.json()
            for item in res_json['members']:
                try:
                    email = item['profile']['email']
                except KeyError:
                    email = None

                if email is not None:
                    emails.append(email)

        return emails


class SlackForm(forms.Form):
    team_token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Team Token'}),
        help_text='You can get your team token <a href="https://get.slack.help/hc/en-us/articles/215770388-Creating-and-regenerating-API-tokens" target="_blank">here</a>')
    name = forms.CharField(widget=forms.HiddenInput())
