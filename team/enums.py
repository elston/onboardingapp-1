
import services

SERVICES = ()
for service in services.__all__:
    SERVICES += ((service, service),)