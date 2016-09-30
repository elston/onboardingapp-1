import os


SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
services_list = os.listdir(SITE_ROOT + "/services")
ignore_list = [
    "__init__.py",
    "common.py",
    "templates",
    "migrations",
    "templatetags",
    "BaseService.py"
]

__all__ = []

for service in services_list:
    if service not in ignore_list and ".pyc" not in service:
        service = service.replace(".py", "")
        __all__ += [service, ]
