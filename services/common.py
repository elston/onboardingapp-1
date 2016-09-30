import base64
import hashlib
import random
from django.conf import settings

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from team.models import AdditionalInfo


def get_slug(name):
    '''
    get slug from the string
    '''
    name = name.lower()
    name = name.replace(' ', '-')

    return name


def check_service_instance(team, name, token, org_name=None,
                           team_name=None, team_id=None):

    instance = None
    services_list = team.service.filter(
        name=name,
        org_name=org_name,
        team_name=team_name,
        team_id=team_id,
        is_active=True
    )

    for item in services_list:
        if decrypt_data(item.token) == token:
            instance = item
            break

    if instance:
        return True
    else:
        return False


def check_service_teamuser(service, teams_list):

    instance = None
    for team in teams_list:
        instance = check_service_instance(
            team,
            service.name,
            service.token,
            service.org_name,
            service.team_name,
            service.team_id
        )

        if instance:
            return True

    return False


def check_services(instance, service):

    if instance.name == service.name and \
       decrypt_data(instance.token) == decrypt_data(service.token) and \
       instance.org_name == service.org_name and \
       instance.team_name == service.team_name and \
       instance.team_id == service.team_id:
        return True
    else:
        return False


def encrypt_data(string):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    password = bytes(hashlib.sha1(salt + settings.SECRET_KEY).hexdigest())

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt),
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(bytes(string))
    result = salt + "$" + token

    return result


def decrypt_data(string):
    salt, data = string.split('$')
    password = bytes(hashlib.sha1(salt + settings.SECRET_KEY).hexdigest())

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt),
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    result = f.decrypt(bytes(data))

    return result


def get_additional_info(teamuser, team, service):
    data = None
    info = AdditionalInfo.objects.filter(
        user=teamuser, team=team, service=service)

    if info:
        data = info[0].data

    return data
