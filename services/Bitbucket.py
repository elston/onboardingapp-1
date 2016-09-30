import requests

from django import forms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service, TeamUser
from team.common import update_error_log, check_emails_list_for_team_members
from services.common import get_slug, check_service_instance
from services.common import encrypt_data, decrypt_data, get_additional_info

BITBUCKET_ERRORS = {
    401: 'Password is incorrect. Please check again!',
    'no-org': 'There is no such organization. Please check again!',
}


class Bitbucket:
    def get_form(self):
        return BitbucketForm(initial={'name': 'Bitbucket'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = BitbucketForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            group_slug = self.check(form, team)

            if group_slug:
                instance = check_service_instance(
                    Team.objects.get(id=t_id),
                    s_name,
                    form.cleaned_data['password'],
                    group_slug
                )

                if not instance:
                    service = self.create(form, s_name, group_slug)
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
        url = 'https://api.bitbucket.org/1.0/groups/%s/' % \
              team.owner.email
        res = requests.get(url=url,
                           auth=(team.owner.email,
                                 form.cleaned_data['password']))
        flag = False
        if res.status_code != 200:
            form.errors['err'] = BITBUCKET_ERRORS[res.status_code]
            # form.errors['password'] = BITBUCKET_ERRORS[res.status_code]
        else:
            res_json = res.json()

            group_slug = get_slug(form.cleaned_data['group_name'])
            for group in res_json:
                if group['slug'] == group_slug:
                    flag = True
                    return group_slug

            if not flag:
                form.errors['err'] = BITBUCKET_ERRORS['no-org']
                # form.errors['group_name'] = BITBUCKET_ERRORS['no-org']

        return None

    def create(self, form, s_name, group_slug):
        token = encrypt_data(form.cleaned_data['password'])
        service = Service()
        service.name = s_name
        service.token = token
        service.org_name = group_slug
        service.save()

        return service

    def add_member_group(self, team, service):
        '''
        add team members to bitbucket with their emails
        '''
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        accountemail = team.owner.email
        email = teamuser.email
        username = get_additional_info(teamuser, team, service)

        if username:
            url = 'https://api.bitbucket.org/1.0/groups/%s/%s/members/%s' % (
                accountemail, service.org_name, username)
        else:
            url = 'https://api.bitbucket.org/1.0/groups/%s/%s/members/%s' % (
                accountemail, service.org_name, email)

        data = '{}'
        header = {'Content-Type': 'application/json'}

        r = requests.put(
            url=url,
            auth=(accountemail, decrypt_data(service.token)),
            data=data,
            headers=header
        )

        if r.status_code != requests.codes.ok:
            update_error_log(teamuser, team, service, r.text)

    def delete_membership_individual(self, email, service, **kwargs):
        team = kwargs['team']
        accountemail = team.owner.email
        teamuser = get_object_or_404(TeamUser, email=email)
        username = get_additional_info(teamuser, team, service)

        if username:
            url = 'https://api.bitbucket.org/1.0/groups/%s/%s/members/%s' % (
                accountemail, service.org_name, username)
        else:
            url = 'https://api.bitbucket.org/1.0/groups/%s/%s/members/%s' % (
                accountemail, service.org_name, email)

        requests.delete(url=url,
                        auth=(accountemail, decrypt_data(service.token)))

    def get_members_list(self, accountemail, service):
        url = 'https://api.bitbucket.org/1.0/groups/%s/%s/members' % (
            accountemail, service.org_name
        )

        r = requests.get(url=url,
                         auth=(accountemail, decrypt_data(service.token)))

        members_list = []
        if r.status_code == requests.codes.ok:
            res_json = r.json()

            for item in res_json:
                members_list.append(item['username'])

        return members_list

    def get_emails_from_members_list(self, accountemail, service, members):
        emails = []

        for item in members:
            res_json = {}
            url = 'https://api.bitbucket.org/1.0/users/%s/emails' % (item)
            r = requests.get(url=url,
                             auth=(accountemail, decrypt_data(service.token)))
            if r.status_code == requests.codes.ok:
                res_json = r.json()

            if res_json:
                emails.append(res_json[0]['email'])

        return emails

    def get_members_email(self, service, **kwargs):
        accountemail = kwargs['team'].owner.email
        members_list = self.get_members_list(accountemail, service)
        emails_list_raw = self.get_emails_from_members_list(
            accountemail, service, members_list
        )

        return emails_list_raw


class BitbucketForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'required': True, 'placeholder': 'Password on Bitbucket'}))
    group_name = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Group Name'}))
    name = forms.CharField(widget=forms.HiddenInput())
