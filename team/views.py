import hashlib
import datetime
import random
import stripe
import json
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.dispatch import receiver
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from allauth.account.signals import user_signed_up
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy

from organization.models import Organization

import services
from services import *
from services.common import check_service_teamuser, check_services

from .models import (
    Service, Team, TeamUser, Account, AdditionalInfo, ErrorLog
)
from .common import check_emails_list_for_team_members
from .common import send_email_message
from .forms import UserInviteForm, CreateTeamForm1, CreateTeamForm2


class TeamsList(ListView):
    template_name = 'team/teams.html'
    context_object_name = 'teams'

    def get_context_data(self, **kwargs):
        context = super(TeamsList, self).get_context_data(**kwargs)

        orgs = Organization.objects.filter(owner=self.request.user)
        context['orgs'] = orgs

        if orgs:
            context['form'] = CreateTeamForm1(user=self.request.user)
        else:
            context['form'] = CreateTeamForm2()

        filter = self.request.GET.get('filter', None)
        if filter:
            context['filter'] = int(filter)
            if int(filter) > 0:
                org = get_object_or_404(Organization, id=int(filter))
                context['organization'] = org

        return context

    def get_queryset(self):
        filter = int(self.request.GET.get('filter', -1))
        org = None

        if filter == -1:
            return Team.objects.filter(
                Q(owner=self.request.user) | Q(member=self.request.user)).distinct()

        if filter > 0:
            org = get_object_or_404(Organization, id=filter)
            return Team.objects.filter(organization_team=org)

        if filter == -2:
            return Team.objects.filter(owner=self.request.user)

        if filter == -3:
            return Team.objects.filter(member=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TeamsList, self).dispatch(request, *args, **kwargs)


@receiver(user_signed_up)
def registation_redirect(sender, **kwargs):
    request = kwargs['request']
    request.session['register'] = True


def check_registration(request):
    register = request.session.get('register', None)

    if register:
        pass

    return redirect(reverse_lazy('dashboard'))


@login_required
def dashboard(request):
    template_name = 'dashboard.html'
    teamowner = request.user
    teams = Team.objects.filter(owner=teamowner)
    services_list = []
    data = {}

    for team in teams:
        services = Service.objects.filter(team_service=team)
        members = team.member.all()
        services_list.extend(services)

        for service in services:
            data[service.id] = list(members)

    for service in services_list:
        for item in services_list:
            if check_services(service, item) and (service.id != item.id):
                data[service.id].extend(data[item.id])
                services_list.remove(item)
                del data[item.id]

    result = {}
    for key, item in data.items():
        service = get_object_or_404(Service, id=key)
        unique_members_set = set(item)
        unique_members = list(unique_members_set)
        result[service] = len(unique_members)

    context = {
        'teams': teams,
        'services_list': result
    }
    return render(request, template_name, context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def get_members_email(request):
    t_id = request.POST.get('t_id')
    team = get_object_or_404(Team, id=t_id)
    services = team.service.all()

    emails_raw = []
    for service in services:
        ObjClass = getattr(eval(service.name), service.name)()
        emails_list = ObjClass.get_members_email(service, team=team)
        emails_raw.extend(emails_list)

    emails = check_emails_list_for_team_members(emails_raw, team.member.all())

    data = {'emails': emails}
    return JsonResponse(data, status=200)


@login_required
def team_info(request, id):
    template_name = 'team/team_info.html'
    team = get_object_or_404(Team, id=id)

    admins = team.admin.all()

    if request.user != team.owner and request.user not in admins:
        raise Http404

    members = team.member.all()
    team_services = team.service.all()

    error_log = ErrorLog.objects.filter(team=team).order_by('user')

    other_services = services.__all__
    other_services.sort()

    organization = Organization.objects.get(team=team)

    form = UserInviteForm(initial={'team': team.pk})

    context = {
        'team': team,
        'members': members,
        'admins': admins,
        'services': team_services,
        'error_log': error_log,
        'other_services': other_services,
        'organization': organization,
        'invite_form': form,
    }

    return render(request, template_name, context)


@login_required
def add_admin(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(TeamUser, id=user_id)

    if request.user != team.owner:
        raise Http404

    team.admin.add(user)
    return redirect(reverse_lazy('team_info', kwargs={'id': team_id}))


@login_required
def remove_admin(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(TeamUser, id=user_id)

    if request.user != team.owner:
        raise Http404

    team.admin.remove(user)
    return redirect(reverse_lazy('team_info', kwargs={'id': team_id}))

@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.owner:
        raise Http404

    team.delete()
    return redirect(reverse_lazy('dashboard'))


@login_required
def myteam_info(request, id):
    team = Team.objects.filter(id=id, member__email=request.user.email)
    template_name = 'team/myteam_info.html'

    if team:
        team = team[0]

        admins = team.admin.all()
        if request.user in admins:
            return redirect(reverse_lazy('team_info', kwargs={'id': team.id}))

        members = team.member.all()
        services = team.service.all()

        context = {
            'team': team,
            'members': members,
            'services': services
        }
        return render(request, template_name, context)

    else:
        err = 'You are not a member of this team or team doesn\'t exist!'
        messages.error(request, err)
        return redirect(reverse_lazy('dashboard'))


@login_required
def additional_info(request, id):
    template_name = 'user/additional_info.html'
    team = Team.objects.filter(id=id, member__email=request.user.email)
    if team:
        team = team[0]
        services = team.service.all()

        additional_info_list = []
        for service in services:
            info = AdditionalInfo.objects.filter(
                user=request.user, team=team, service=service
            )
            additional_info_list.extend(info)

        result = {}
        for service in services:
            flag = False
            for info in additional_info_list:
                if info.service == service:
                    result[service] = info
                    flag = True

            if not flag:
                result[service] = None

        context = {
            'team': team,
            'services': services,
            'additional_info_list': additional_info_list,
            'result': result
        }
        return render(request, template_name, context)

    else:
        raise Http404


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def add_additional_info(request, id):
    team = get_object_or_404(Team, id=id)
    service_id = request.POST.get('key') or False
    data = request.POST.get('data') or ''

    members = team.member.all()
    if request.user not in members:
        messages.error(request, 'You are not a member of this team!')
        return JsonResponse({}, status=400)

    if service_id:
        service = get_object_or_404(Service, id=service_id)
    else:
        messages.error(request, 'The service is not found.')
        return JsonResponse({}, status=400)

    try:
        info = AdditionalInfo.objects.get(
            user=request.user, team=team, service=service
        )
    except:
        info = None

    if info:
        info.data = data
        info.save()

    if data and not info:
        info = AdditionalInfo()
        info.user = request.user
        info.team = team
        info.service = service
        info.data = data
        info.save()

    messages.success(request, 'Information is saved successfully!')
    return JsonResponse({}, status=200)


@login_required
@require_http_methods(["POST"])
def remove_error_log(request, id):
    error_log = get_object_or_404(ErrorLog, id=id)
    team = error_log.team
    admins = team.admin.all()

    if team.owner != request.user and request.user not in admins:
        raise Http404

    teamuser = error_log.user
    error_log.delete()

    messages.success(request, 'Error Log for user %s is removed.' % teamuser)
    return redirect(reverse_lazy('team_info', kwargs={'id': team.id}))


@login_required
def update_account(request):
    template_name = 'user/update_account.html'
    teamuser = TeamUser.objects.get(email=request.user.email)
    account = teamuser.account

    other_accounts = Account.objects.all()
    if account:
        other_accounts = other_accounts.exclude(id__in=[account.id])

    context = {
        'accounts': other_accounts,
        'email': teamuser.email,
        'customer_id': teamuser.customer_id,
        'key': settings.STRIPE_KEYS['publishable_key']
    }

    return render(request, template_name, context)


@login_required
def charge_account(request):
    teamuser = TeamUser.objects.get(email=request.user.email)
    account = Account.objects.get(id=request.POST.get('a_id'))

    card = request.POST.get('stripeToken')
    stripe.api_key = settings.STRIPE_KEYS['stripe_secret_key']

    if not card:  # update subscription
        subscription = stripe.Subscription.retrieve(teamuser.subscription_id)
        subscription.plan = account.stripe_id
        subscription.save()
    else:  # for the first time
        customer = stripe.Customer.create(
            email=teamuser.email,
            plan=account.stripe_id,
            card=card
        )

        teamuser.customer_id = customer.id
        teamuser.subscription_id = customer.subscriptions.data[0].id
        teamuser.last4_card_num = customer.sources.data[0].last4
        teamuser.exp_date = datetime.date.today() + timedelta(days=30)

    teamuser.account = account
    teamuser.save()

    return redirect(reverse_lazy('plan'))


@login_required
def plan(request):
    template_name = 'user/plan.html'
    teamuser = TeamUser.objects.get(email=request.user.email)
    account = teamuser.account

    context = {
        'teamuser': teamuser,
        'account': account
    }

    return render(request, template_name, context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def cancel_account(request):
    teamuser = TeamUser.objects.get(email=request.user.email)
    teamuser.account = None
    teamuser.customer_id = None
    teamuser.save()

    stripe.api_key = settings.STRIPE_KEYS['stripe_secret_key']
    subscription = stripe.Subscription.retrieve(teamuser.subscription_id)
    subscription.delete(at_period_end=True)

    messages.success(request, 'The account is canceled successfully!')
    return JsonResponse({}, status=200)


@login_required
def accept_invitation_step1(request, m_id, t_id):
    teamuser = get_object_or_404(TeamUser, id=m_id)
    if teamuser != request.user:
        messages.error(request, 'You don\'t have permission')
        url = request.path
        logout(request)
        return redirect(reverse_lazy('account_login')+'?next='+url)

    team = Team.objects.filter(id=t_id, member=teamuser)
    if team:
        team = team[0]
        services = team.service.all()

        #if there are no services for the team, skip step one.
        if not services:
            return redirect(reverse_lazy('accept_invitation_step2',
                                         kwargs={'m_id': m_id, 't_id': t_id}))

        additional_info_list = []
        for service in services:
            info = AdditionalInfo.objects.filter(
                user=request.user, team=team, service=service
            )
            additional_info_list.extend(info)

        result = {}
        for service in services:
            flag = False
            for info in additional_info_list:
                if info.service == service:
                    result[service] = info
                    flag = True

            if not flag:
                result[service] = None

        context = {
            'team': team,
            'services': services,
            'additional_info_list': additional_info_list,
            'result': result,
            'accept_invitation': True
        }
        return render(request, 'user/additional_info.html', context)

    else:
        err = 'You are not a member of this team or team doesn\'t exist!'
        messages.error(request, err)
        return redirect(reverse_lazy('dashboard'))


@login_required
def accept_invitation_step2(request, m_id, t_id):
    teamuser = get_object_or_404(TeamUser, id=m_id)

    if teamuser != request.user:
        messages.error(request, 'You don\'t have permission')
        url = request.path
        logout(request)
        return redirect(reverse_lazy('account_login'), kwargs={'next': url})

    team = Team.objects.filter(id=t_id, member=teamuser)
    if team:
        team = team[0]
        services = team.service.all()

        # send invitation for services
        for service in services:
            ObjClass = getattr(eval(service.name), service.name)()
            ObjClass.add_member_individual(teamuser, service, team)

        context = {
            'teamuser': teamuser,
            'services': services,
            'team': team
        }

        return render(request, 'user/accept_invitation.html', context)

    else:
        err = 'You are not a member of this team or team doesn\'t exist!'
        messages.error(request, err)
        return redirect(reverse_lazy('dashboard'))


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def check_team_limit(request):
    teams = request.user.owner.all()

    if teams:
        if request.user.account:
            teams_count = Team.objects.filter(owner=request.user).count()
            if teams_count >= request.user.account.team_limit:
                response = 'Team limit!'
                return JsonResponse({'response': response}, status=400)
        else:
            response = 'Please update your account!'
            return JsonResponse({'response': response}, status=400)

    return JsonResponse({}, status=200)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_team(request):
    orgs = Organization.objects.filter(owner=request.user).exists()

    if orgs:
        form = CreateTeamForm1(request.POST)
    else:
        form = CreateTeamForm2(request.POST)

    if form.is_valid():
        org = form.cleaned_data['organization']

        if isinstance(org, Organization):
            if org.owner != request.user:
                messages.error(request, 'You don\'t have permission')
                return JsonResponse({}, status=403)
        else:
            org = Organization(name=form.cleaned_data['organization'])
            org.owner = request.user
            org.save()

        team = Team()
        team.owner = request.user
        team.name = form.cleaned_data['team_name']
        team.description = form.cleaned_data['team_description']
        team.save()

        org.team.add(team)
        org.save()

        messages.success(request, 'The team {} was created successfully'.format(team.name))
        data = {'href': '/team/' + str(team.id)}
        return JsonResponse(data, status=200)

    else:
        response = {}
        for k in form.errors:
            response[k] = form.errors[k][0]

        return JsonResponse({'response': response}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def remove_member(request):
    t_id = request.POST.get('t_id')
    team = None

    try:
        team = Team.objects.get(id=t_id)
    except Team.DoesNotExist:
        messages.error(request, 'Team does not exist')
        return JsonResponse({}, status=404)

    if team:
        admins = team.admin.all()

    if not team or (request.user != team.owner and request.user not in admins):
        messages.error(request, 'You don\'t have permission')
        return JsonResponse({}, status=403)

    m_id = request.POST.get('m_id')

    teamuser = TeamUser.objects.get(id=m_id)
    team.member.remove(m_id)
    team.admin.remove(m_id)

    teams_list = Team.objects.filter(member=teamuser)

    # remove all service from him
    for service in team.service.all():
        # remove member from service
        ObjClass = getattr(eval(service.name), service.name)()
        instance = check_service_teamuser(service, teams_list)

        if not instance:
            ObjClass.delete_membership_individual(
                teamuser.email, service, team=team)

        # remove additional info for service
        info = AdditionalInfo.objects.filter(
            user=teamuser, team=team, service=service
        )
        for item in info:
            item.delete()

    messages.success(request, 'The member is removed successfully!')
    return JsonResponse({}, status=200)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def invite_user(request):
    form = UserInviteForm(request.POST)

    if form.is_valid():
        try:
            team = Team.objects.get(id=form.cleaned_data['team'])
        except Team.DoesNotExist:
            messages.error(request, 'Team does not exist')
            return JsonResponse({}, status=404)

        admins = team.admin.all()

        if request.user != team.owner and request.user not in admins:
            messages.error(request, 'You don\'t have permission')
            return JsonResponse({}, status=403)

        user_email = form.cleaned_data['user_email']
        tusers = TeamUser.objects.filter(email=user_email)

        if tusers:
            teamuser = tusers[0]
            email_body = """
            You've got an invitation to join Team: <b>%s</b> <br />
            You can use all services from the team once you accept the invitation at the following link <br /><br />
            http://www.allstacks.com/team/%i/member/%i/accept-invitation-step1 <br /> <br />
            Thank you, <br />
            Allstacks team
            """ % (team.name, team.id, teamuser.id)
        else:
            # generate temporary password
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            password = hashlib.sha1(salt+user_email).hexdigest()

            teamuser = TeamUser()
            teamuser.username = user_email.split('@')[0]
            teamuser.email = user_email
            teamuser.password = make_password(password)
            teamuser.is_temp = True
            teamuser.first_name = form.cleaned_data['first_name']
            teamuser.last_name = form.cleaned_data['last_name']
            teamuser.save()

            email_body = """
            You've got an invitation to join <i>Team</i>: %s <br />
            You can use all services from the team once you accept the invitation at the following link <br /><br />
            http://www.allstacks.com/team/%i/member/%i/accept-invitation-step1 <br /><br />
            You can login the system with following credentials <br />
            <i>Username:</i> %s <br />
            <i>Temporary password:</i> %s <br /><br />
            Once you accept the invitation, please update your password! <br /><br />
            Thank you, <br />
            Allstacks team""" % (team.name,
                team.id, teamuser.id, teamuser.email, password
            )

        # check he is already there
        team.member.add(teamuser)

        if form.cleaned_data['admin']:
            team.admin.add(teamuser)

        team.save()

        if len(teamuser.first_name) > 0:
            header_string = 'Dear {},'.format(teamuser.first_name)
        else: 
            header_string = 'Dear {},'.format(teamuser.email)

        send_email_message(email_body, header_string, 'Allstacks Team Invitation for {}'.format(team.name), user_email)

        messages.success(request, 'The user is invited successfully!')
        return JsonResponse({}, status=200)

    else:
        response = {}
        for k in form.errors:
            response[k] = form.errors[k][0]

        return JsonResponse({'response': response}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def get_form(request):
    s_name = request.POST.get('s_name', None)

    if s_name:
        ObjClass = getattr(eval(s_name), s_name)()
        form = ObjClass.get_form()

        response = []
        for item in form:
            help_text = ''
            if item.help_text:
                help_text = '<span class="helptext">' + \
                            item.help_text + '</span>'
            input_text = str(item)
            response.append(input_text + help_text)

        return JsonResponse({'form': response}, status=200)

    return JsonResponse({}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def search_service(request):
    name = request.POST.get('search', None)
    services_list = services.__all__

    if name:
        result = []
        for service in services_list:
            if service.lower().find(name.lower()) != -1:
                result.append(service)

    else:
        result = services_list

    return JsonResponse({'services': result}, status=200)


@login_required
def add_service(request, id):
    template_name = 'team/tools.html'
    team = get_object_or_404(Team, id=id)
    admins = team.admin.all()

    if request.user != team.owner and request.user not in admins:
        raise Http404

    other_services = services.__all__
    other_services.sort()

    context = {
        'team': team,
        'other_services': other_services
    }

    return render(request, template_name, context)


@require_http_methods(["POST"])
@login_required
def add_service_real(request, s_name, t_id):
    team = get_object_or_404(Team, id=t_id)
    admins = team.admin.all()

    if request.user != team.owner and request.user not in admins:
        raise Http404

    ObjClass = getattr(eval(s_name), s_name)()

    return ObjClass.Process(request, s_name, t_id)


@login_required
def add_service_auth_finish(request, s_name):
    t_id = request.session.pop('t_id', None)

    if t_id:
        team = get_object_or_404(Team, id=t_id)
        admins = team.admin.all()
        if request.user != team.owner and request.user not in admins:
            raise Http404

        ObjClass = getattr(eval(s_name), s_name)()
        return ObjClass.auth_finish(request, s_name, team)

    raise Http404


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def remove_group_service(request, t_id, s_name):
    team = get_object_or_404(Team, id=t_id)

    services = team.service.filter(name=s_name)
    admins = team.admin.all()

    if request.user != team.owner and request.user not in admins:
        messages.error(request, 'You don\'t have permission')
        return JsonResponse({}, status=403)

    for service in services:
        remove_service_real(team, service)

    messages.success(request, 'The group service is removed successfully!')
    return JsonResponse({}, status=200)


def remove_service_real(team, service):
    ObjClass = getattr(eval(service.name), service.name)()

    team.service.remove(service.id)

    service.is_active = False
    service.save()

    admins = team.admin.all()

    for member in team.member.all():

        # remove additional info for service
        info = AdditionalInfo.objects.filter(
            user=member, team=team, service=service
        )
        for item in info:
            item.delete()

        # remove member from service, if member is not admin
        if member not in admins:
            ObjClass.delete_membership_individual(
                member.email, service, team=team)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def remove_service(request):
    t_id = request.POST.get('t_id')
    team = None

    try:
        team = Team.objects.get(id=t_id)
    except Team.DoesNotExist:
        messages.error(request, 'Team does not exist')
        return JsonResponse({}, status=404)

    if team:
        admins = team.admin.all()

    if not team or (request.user != team.owner and request.user not in admins):
        messages.error(request, 'You don\'t have permission')
        return JsonResponse({}, status=403)

    s_id = request.POST.get('s_id')
    service = Service.objects.get(id=s_id)

    remove_service_real(team, service)

    messages.success(request, 'The service is removed successfully!')
    return JsonResponse({}, status=200)


def stripe_webhook(request):
    # Retrieve the request's body and parse it as JSON
    event_json = json.loads(request.body)

    # Verify the event by fetching it from Stripe
    event = stripe.Event.retrieve(event_json["id"])

    # print event,'#########'
    # Do something with event
    # update exp_date and handle card failures

    return JsonResponse({}, status=200)
