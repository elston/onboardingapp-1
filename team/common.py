from .models import ErrorLog


from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def update_error_log(teamuser, team, service, errortext):
    error_log = ErrorLog()
    error_log.user = teamuser
    error_log.team = team
    error_log.service = service
    error_log.text = errortext
    error_log.save()


def send_email_message(email_body, email_header, email_subject, user_email):
    html_message = render_to_string(
        'email_template.html',
        {'emailheader': email_header, 'emailbody': email_body}
    )
    send_mail(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False,
        html_message=html_message
    )


def check_emails_list_for_team_members(emails_list, team_members):
    result = []

    emails_list_set = set(emails_list)
    team_emails_set = set()

    for member in team_members:
        team_emails_set.add(member.email)

    result = list(emails_list_set - team_emails_set)

    return result
