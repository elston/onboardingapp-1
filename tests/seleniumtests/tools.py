from string import lowercase, digits
from random import choice
from functools import wraps
import inspect

from unittest import skipUnless

from settings import EMAIL_DOMAIN, TEST_SUITS_TO_RUN


def randstr(length, letters=True, numbers=False):
    charset = []
    if letters:
        charset += lowercase
    if numbers:
        charset += digits

    return ''.join([choice(charset) for _ in range(length)])


def randemail(length, letters=True, numbers=True, domain=None):
    return '%s%s' % (randstr(length, letters, numbers), domain or EMAIL_DOMAIN)


# decorator. ensures chained method syntactic sugar
def chained_method(method):
    @wraps(method)
    def wrapper(*args, **kw):

        # filter out class and static methods
        # TODO static methods may pass. e.g. chained_method(lambda(x): x)(12)
        if not args or args and inspect.isclass(args[0]):
            raise TypeError('Only instance methods can be chained')

        self = args[0]
        if method(*args, **kw) is not self:
            raise NotImplementedError('Chained method returns no self object')
        return self

    return wrapper


# silence assertions in chains
def hush(callback, exception, err_cb=None):
    try:
        return callback()
    except exception:
        if err_cb:
            err_cb()

    return False


class RegisterTest(object):

    def __init__(self, *tests_to_run):
        self.__tests_to_run__ = tests_to_run

    def __call__(self, test_name, message='configured out'):

        def decorator(method):

            return skipUnless(test_name in self.__tests_to_run__, message)(method)

        return decorator


def register_test_case(test_name, message='suit configured out'):

    def decorator(method):

        return skipUnless(test_name in TEST_SUITS_TO_RUN, message)(method)

    return decorator
