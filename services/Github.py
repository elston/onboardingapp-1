import requests

from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service, TeamUser
from team.common import update_error_log, check_emails_list_for_team_members
from .common import (
    check_service_instance, encrypt_data, decrypt_data, get_additional_info
)

GITHUB_ERRORS = {
    'Bad credentials':
    'The token you provided is not correct. Please check again!',
    'Not Found': 'There is no such organization. Please check again!',
}


class Github:
    def get_form(self):
        return GithubForm(initial={'name': 'Github'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = GithubForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            team_id = self.check(form)

            if team_id:
                instance = check_service_instance(
                    team, s_name,
                    form.cleaned_data['token'],
                    form.cleaned_data['org_name'],
                    form.cleaned_data['team_name'],
                    team_id
                )

                if not instance:
                    service = self.create(form, s_name, team_id)
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
        url = 'https://api.github.com/orgs/%s/teams' % \
              form.cleaned_data['org_name']
        header = {
            "Authorization": "token " + form.cleaned_data['token']
        }

        res = requests.get(url=url, headers=header)
        res_json = res.json()

        if type(res_json) is dict:
            form.errors['err'] = GITHUB_ERRORS[res_json['message']]
            # if res_json['message'] == 'Bad credentials':
            #     form.errors['token'] = GITHUB_ERRORS[res_json['message']]
            # if res_json['message'] == 'Not Found':
            #     form.errors['org_name'] = GITHUB_ERRORS[res_json['message']]
        else:
            team_id = None
            for team in res_json:
                if team['name'] == form.cleaned_data['team_name']:
                    team_id = team['id']
                    return team_id

            if not team_id:
                err = 'There is no such team. Please check again!'
                form.errors['err'] = err
                # form.errors['team_name'] = err

        return None

    def create(self, form, s_name, team_id):
        token = encrypt_data(form.cleaned_data['token'])
        service = Service()
        service.name = s_name
        service.token = token
        service.org_name = form.cleaned_data['org_name']
        service.team_name = form.cleaned_data['team_name']
        service.team_id = team_id
        service.save()

        return service

    def add_member_group(self, team, service):
        '''
        send invitations to team members to github with their emails
        '''
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        header = {"Authorization": "token " + decrypt_data(service.token)}

        username = get_additional_info(teamuser, team, service)
        if username:
            url = 'https://api.github.com/teams/%s/memberships/%s' % \
                  (service.team_id, username)
            res = requests.put(url=url, headers=header)

            if res.status_code != requests.codes.ok:
                update_error_log(teamuser, team, service, res.text)
        else:
            email = teamuser.email
            member_login = self.get_member_name_with_email(email)
            if member_login:
                url = 'https://api.github.com/teams/%s/memberships/%s' % \
                      (service.team_id, member_login)
                res = requests.put(url=url, headers=header)

                if res.status_code != requests.codes.ok:
                    update_error_log(teamuser, team, service, res.text)

            else:
                e = "Email %s did not correspond to a user" % (email)
                update_error_log(teamuser, team, service, e)

    def get_member_name_with_email(self, email):
        '''
        get login from an existing user on github with his email.
        return login if success, empty string if not
        '''
        url = 'https://api.github.com/search/users?q=%s+in%%3Aemail' % email
        res = requests.get(url=url)
        res_json = res.json()

        if int(res_json['total_count']) == 0:
            return None
        else:
            return res_json['items'][0]['login']

    def delete_membership_individual(self, email, service, **kwargs):
        '''
        delete membership of the user to github service with his email.
        '''
        header = {"Authorization": "token " + decrypt_data(service.token)}

        team = kwargs['team']
        teamuser = get_object_or_404(TeamUser, email=email)
        username = get_additional_info(teamuser, team, service)
        if username:
            url = 'https://api.github.com/teams/%s/memberships/%s' % (
                service.team_id, username)
            requests.delete(url=url, headers=header)
        else:
            member_login = self.get_member_name_with_email(email)
            if member_login:
                url = 'https://api.github.com/teams/%s/memberships/%s' % (
                    service.team_id, member_login)
                requests.delete(url=url, headers=header)

    def get_members_list(self, service):
        url = 'https://api.github.com/teams/%s/members' % (service.team_id)
        header = {"Authorization": "token " + decrypt_data(service.token)}
        res = requests.get(url=url, headers=header)

        members_list = []
        if res.status_code == requests.codes.ok:
            res_json = res.json()

            for item in res_json:
                members_list.append(item['login'])

        return members_list

    def get_emails_from_members_list(self, members_list):
        emails = []

        for item in members_list:
            res_json = {}
            url = 'https://api.github.com/users/%s' % (item)
            res = requests.get(url=url)
            if res.status_code == requests.codes.ok:
                res_json = res.json()

            if res_json:
                email = res_json['email']
                if email is not None:
                    emails.append(email)

        return emails

    def get_members_email(self, service, **kwargs):
        members_list = self.get_members_list(service)
        emails_list_raw = self.get_emails_from_members_list(members_list)

        return emails_list_raw


class GithubForm(forms.Form):
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'token'}),
        help_text='You can get your token <a href="https://github.com/settings/tokens" target="_new">here</a>')
    org_name = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Organization Name'}))
    team_name = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Team Name'}))
    name = forms.CharField(widget=forms.HiddenInput())
