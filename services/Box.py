from django import forms
from django.shortcuts import redirect, Http404
from django.conf import settings
from django.http import JsonResponse
from django.core.urlresolvers import reverse_lazy

from boxsdk import OAuth2, Client

from team.models import Service
from team.common import update_error_log
from .common import encrypt_data, decrypt_data


class Box:
    def get_form(self):
        return BoxForm(initial={'name': 'Box'})

    def Process(self, request, s_name, t_id):
        # form = BoxForm(request.POST)
        request.session['t_id'] = t_id

        oauth = OAuth2(
            client_id=settings.BOX_CLIENT_ID,
            client_secret=settings.BOX_CLIENT_SECRET,
        )
        redirect_uri = 'http://127.0.0.1:8000/service/Box/auth-finish'
        auth_url, csrf_token = oauth.get_authorization_url(redirect_uri)
        request.session['box_csrf_token'] = csrf_token

        return JsonResponse({'redirect': True, 'url': auth_url}, status=200)

    def create(self, s_name, access_token, refresh_token, enterprise, team_id):
        service = Service()
        service.name = s_name
        service.token = encrypt_data(access_token)
        service.org_name = refresh_token
        service.team_name = enterprise
        service.team_id = team_id
        service.save()

        return service

    def auth_finish(self, request, s_name, team):
        if request.GET.get('error'):
            # print request.GET.get('error_description')
            return redirect(reverse_lazy('team_info', kwargs={'id': team.pk}))

        oauth = OAuth2(
            client_id=settings.BOX_CLIENT_ID,
            client_secret=settings.BOX_CLIENT_SECRET,
        )
        code = request.GET.get('code')
        state = request.GET.get('state')

        if state != request.session.pop('box_csrf_token', ''):
            raise Http404

        try:
            access_token, refresh_token = oauth.authenticate(code)
        except Exception as e:
            print e
            return redirect(reverse_lazy('team_info', kwargs={'id': team.pk}))

        client = Client(oauth)
        me = client.user(user_id='me').get()

        try:
            enterprise = me['enterprise']['name']
            team_id = me['enterprise']['id']
        except KeyError:
            enterprise = me['name']
            team_id = me['id']

        instance = team.service.filter(
            name=s_name, team_name=enterprise, team_id=team_id)

        if not instance:
            service = self.create(
                s_name, access_token, refresh_token, enterprise, team_id)
            team.service.add(service)
            team.save()

            self.add_member_group(team, service)

        return redirect(reverse_lazy('team_info', kwargs={'id': team.id}))

    def add_member_group(self, team, service):
        for member in team.member.all():
            self.add_member_individual(member, service, team)

    def add_member_individual(self, teamuser, service, team):
        oauth = OAuth2(
            client_id=settings.BOX_CLIENT_ID,
            client_secret=settings.BOX_CLIENT_SECRET,
            access_token=decrypt_data(service.token)
        )

        client = Client(oauth)
        try:
            client.create_user(teamuser.username, teamuser.email)
        except Exception as e:

            try:
                errortext = "%s: %s (%s, %s)" % (
                    str(e.status), e.message,
                    teamuser.email, teamuser.username)
            except KeyError:
                errortext = e

            update_error_log(teamuser, team, service, errortext)

    def delete_membership_individual(self, email, service, **kwargs):
        member_id = self.get_member_id_with_email(email, service)

        if member_id:
            oauth = OAuth2(
                client_id=settings.BOX_CLIENT_ID,
                client_secret=settings.BOX_CLIENT_SECRET,
                access_token=decrypt_data(service.token)
            )

            client = Client(oauth)
            try:
                client.make_request(
                    'DELETE',
                    'https://api.box.com/2.0/users/%s' % member_id
                )
            except Exception:
                pass

    def get_member_id_with_email(self, email, service):
        member_id = None
        members_list = self.get_members_list(service)
        for member in members_list:
            if member.login == email:
                member_id = member.id
                break

        return member_id

    def get_members_list(self, service):
        users = []

        oauth = OAuth2(
            client_id=settings.BOX_CLIENT_ID,
            client_secret=settings.BOX_CLIENT_SECRET,
            access_token=decrypt_data(service.token)
        )

        client = Client(oauth)
        try:
            users = client.users()
        except Exception as e:
            err = {"error": "invalid_request",
                   "error_description": "No \"refresh_token\" parameter found"}
            if e.message == err:
                oauth = OAuth2(
                    client_id=settings.BOX_CLIENT_ID,
                    client_secret=settings.BOX_CLIENT_SECRET,
                    refresh_token=service.org_name
                )
                access_token, refresh_token = oauth.refresh(
                    decrypt_data(service.token))

                service.token = encrypt_data(access_token)
                service.org_name = refresh_token
                service.save()

                users = self.get_members_list(service)

        return users

    def get_emails_from_members_list(self, service, members_list):
        emails_list = []
        for member in members_list:
            emails_list.append(member.login)

        return emails_list

    def get_members_email(self, service, **kwargs):
        emails_list_raw = self.get_emails_from_members_list(
            service, self.get_members_list(service)
        )
        return emails_list_raw


class BoxForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput())
