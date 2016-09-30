from ..tools import randemail, randstr, RegisterTest, register_test_case

from ..tests import BaseTestCase
from ..page_objects.index import IndexPage
from ..page_objects.signup import SignupPage
from ..page_objects.dashboard import DashboardPage
from ..page_objects.signout import SignoutPage
from ..page_objects.teams import TeamsPage
from ..page_objects.organization import OrganizationPage
from ..page_objects.signout import SignoutPage


@register_test_case('NavigationTestCase')
class NavigationTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_navigation'
    )

    @register_test('test_navigation')
    def test_navigation(self):
        email = randemail(8)
        password = randstr(8)

        (
            IndexPage(self)
                .start()
                .signup(email),

            SignupPage(self)
                .assert_page()
                .signup(email, password)
        )
