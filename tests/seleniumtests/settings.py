__author__ = 'qtlab'

SITE = "localhost:5555"
TEST_ON_PRODUCTION = [
    # True,
    False
].pop()

EMAIL_DOMAIN = '@mailinator.com'

CHROMEDRIVER_PATH = [
    '/opt/google/chrome/chromedriver',  # arquero
].pop()

DRIVER = [
    'chrome'
    # 'firefox'
].pop()

FULL_SCREEN = True

WAIT_PERIOD_LONG = 15  # wait for external requests
WAIT_PERIOD_MIDDLE = 10  # wait for pages
WAIT_PERIOD_SHORT = 5  # wait for elements
WAIT_PERIOD_JOTA = 1  # sleep

TEST_SUITS_TO_RUN = [
    # 'ServicesTestCase',  # ! TODO no service fields on live server, <test_on_production = True> solves the issue
    # 'AccountTestCase',  # ! TODO no payment fields on live server, <test_on_production = True> solves the issue
    'MembersTestCase',
    'NavigationTestCase',
    'OrganizationTestCase',
    'TeamsTestCase',
    'RegisterTestCase',
    'UrlsTestCase',
]
