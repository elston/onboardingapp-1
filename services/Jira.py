from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from jira import JIRA
from jira.exceptions import JIRAError

from team.models import Team, Service, TeamUser
from team.common import update_error_log, check_emails_list_for_team_members
from .common import (
    check_service_instance, encrypt_data, decrypt_data, get_additional_info
)

JIRA_ERRORS = {
    401: 'Password is incorrect. Please check again!',
    502: 'Site Name is incorrect. Please check again!',
}


class Jira:
    def get_form(self):
        return JiraForm(initial={'name': 'Jira'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = JiraForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            sitename = form.cleaned_data['sitename']
            sitename = sitename.replace(';', '')
            jira = self.check(form, sitename)

            if jira:
                instance = check_service_instance(
                    team, s_name,
                    form.cleaned_data['password'],
                    sitename
                )

                if not instance:
                    service = self.create(form, s_name, sitename)
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

    def check(self, form, sitename):
        jira = None

        try:
            options = {'server': 'https://%s.atlassian.net' % sitename}
            jira = JIRA(options,
                        basic_auth=('admin',
                                    form.cleaned_data['password']))
        except JIRAError, e:
            form.errors['err'] = JIRA_ERRORS[e.status_code]

        return jira

    def create(self, form, s_name, sitename):
        token = encrypt_data(form.cleaned_data['password'])
        service = Service()
        service.name = s_name
        service.token = token
        service.org_name = sitename
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        email = teamuser.email
        username = get_additional_info(teamuser, service, team)

        options = {'server': 'https://%s.atlassian.net' % service.org_name}
        jira = JIRA(options, basic_auth=('admin', decrypt_data(service.token)))
        try:
            if username:
                jira.add_user(username, email)
            else:
                jira.add_user(email, email)
        except Exception as e:
            update_error_log(teamuser, team, service, e)

    def delete_membership_individual(self, email, service, **kwargs):
        team = kwargs['team']
        teamuser = get_object_or_404(TeamUser, email=email)
        username = get_additional_info(teamuser, team, service)

        options = {'server': 'https://%s.atlassian.net' % service.org_name}
        jira = JIRA(options, basic_auth=('admin', decrypt_data(service.token)))
        if username:
            jira.delete_user(username)
        else:
            jira.delete_user(email)

    def get_members_email(self, service, **kwargs):
        options = {'server': 'https://%s.atlassian.net' % service.org_name}
        jira = JIRA(options, basic_auth=('admin', decrypt_data(service.token)))
        groups = jira.groups()

        emails_list = []
        for group in groups:
            members = jira.group_members(group)
            for key, value in members.items():
                if value['email'] != 'noreply@atlassian.com':
                    emails_list.append(value['email'])

        emails = set(emails_list)
        emails_list = list(emails)

        return emails_list


class JiraForm(forms.Form):
    sitename = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Atlassian Site Name'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'required': True, 'placeholder': 'Password on Atlasian'}))
    name = forms.CharField(widget=forms.HiddenInput())
