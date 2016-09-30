from ..tools import RegisterTest, register_test_case

from . import BaseTestCase
from ..page_objects.index import IndexPage
from ..page_objects.signup import SignupPage
from ..page_objects.signin import SigninPage
from ..page_objects.dashboard import DashboardPage
from ..page_objects.forgot_password import ForgotPasswordPage
from ..page_objects.signout import SignoutPage


@register_test_case('UrlsTestCase')
class UrlsTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_check_urls'
    )

    @register_test('test_check_urls')
    def test_check_urls(self):
        (
            IndexPage(self)
                .start()
                .assert_page(),

            SignupPage(self)
                .start()
                .assert_page(),

            SigninPage(self)
                .start()
                .assert_page(),

            ForgotPasswordPage(self)
                .start()
                .assert_page(),

            DashboardPage(self)
                .start()
                .assert_page(),
        )
