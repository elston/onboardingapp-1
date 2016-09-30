import requests

from django import forms
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from team.models import Team, Service
from team.common import update_error_log
from .common import check_service_instance, encrypt_data, decrypt_data


class Quay:
    def get_form(self):
        return QuayForm(initial={'name': 'Quay'})

    @csrf_exempt
    def Process(self, request, s_name, t_id):
        form = QuayForm(request.POST)
        if form.is_valid():
            team = get_object_or_404(Team, id=t_id)
            service_team = self.check(form)

            if service_team:
                instance = check_service_instance(
                    team, s_name,
                    form.cleaned_data['token'],
                    form.cleaned_data['organization'],
                    form.cleaned_data['team']
                )

                if not instance:
                    service = self.create(form, s_name)
                    team.service.add(service)
                    team.save()

                    self.add_member_group(team, service)

                    emails_list = self.get_members_email(service)
                    return JsonResponse(
                        {'emails_list': emails_list}, status=200)

                else:
                    form.errors['err'] = 'Second instance of service'

        return JsonResponse(form.errors, status=400)

    def check(self, form):
        url = 'https://quay.io/api/v1/organization/%s' % \
              form.cleaned_data['organization']
        header = {"Authorization": 'Bearer ' + form.cleaned_data['token']}
        res = requests.get(url, headers=header)

        res_json = res.json()
        if res.status_code != 200:
            if res.status_code == 404:
                err = 'There is no such organization. Please check again!'
            else:
                err = res_json['error_message']

            form.errors['err'] = err
            return None

        try:
            team = res_json['teams'][form.cleaned_data['team']]
            return team
        except:
            err = 'There is no such team. Please check again!'
            form.errors['err'] = err
            return None

    def create(self, form, s_name):
        service = Service()
        service.name = s_name
        service.token = encrypt_data(form.cleaned_data['token'])
        service.org_name = form.cleaned_data['organization']
        service.team_name = form.cleaned_data['team']
        service.save()

        return service

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        url = 'https://quay.io/api/v1/organization/%s/team/%s/invite/%s' % (
            service.org_name, service.team_name, teamuser.email)
        header = {"Authorization": 'Bearer ' + decrypt_data(service.token)}
        res = requests.put(url, headers=header)

        if res.status_code != 200:
            update_error_log(teamuser, team, service, res.text)

    def delete_membership_individual(self, email, service, **kwargs):
        url = 'https://quay.io/api/v1/organization/%s/team/%s/invite/%s' % (
            service.org_name, service.team_name, email)
        header = {"Authorization": 'Bearer ' + decrypt_data(service.token)}
        requests.delete(url, headers=header)

    def get_members_email(self, service, **kwargs):
        return []


class QuayForm(forms.Form):
    token = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Token'}))
    organization = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Organization'}))
    team = forms.CharField(
        widget=forms.TextInput(attrs={'required': True,
                                      'placeholder': 'Team name'}))
    name = forms.CharField(widget=forms.HiddenInput())
