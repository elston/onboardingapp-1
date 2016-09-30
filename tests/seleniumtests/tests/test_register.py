from ..tests import BaseTestCase

from ..page_objects.side_bar import SideBarPage
from ..page_objects.dashboard import DashboardPage
from ..page_objects.headers import SignedInHeaderPage
from ..page_objects.signout import SignoutPage
from ..page_objects.signin import SigninPage
from ..page_objects.signup import SignupPage
from ..page_objects.change_pasword import ChangePasswordPage
from ..page_objects.forgot_password import ForgotPasswordPage
from ..page_objects.pass_reset_done import PassResetDonePage

from ..tools import randstr, randemail, RegisterTest, register_test_case


@register_test_case('RegisterTestCase')
class RegisterTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_logout',
        'test_change_password',
        'test_forgot_password',
    )

    @register_test('test_logout')
    def test_logout(self):
        email, password = help_register(self)

        (
            DashboardPage(self)
                .assert_page(),

            SignedInHeaderPage(self)
                .logout(),

            SignoutPage(self)
                .assert_page()
                .go_back(),

            SideBarPage(self)
                .open()
                .logout(),

            SignoutPage(self)
                .assert_page()
                .signout(),

            SigninPage(self)
                .assert_page()
                .signin(email, password)
                .assert_page(False),

            DashboardPage(self)
                .assert_page(),
        )

    @register_test('test_change_password')
    def test_change_password(self):
        email, old_password = help_register(self)
        new_password = randstr(8)

        (
            DashboardPage(self)
                .assert_page(),

            SideBarPage(self)
                .open()
                .to_settings(),

            ChangePasswordPage(self)
                .assert_page()
                .change_password(old_password, new_password),

            SignedInHeaderPage(self)
                .logout(),

            SignoutPage(self)
                .assert_page()
                .signout(),

            SigninPage(self)
                .assert_page()
                .signin(email, old_password)
                .assert_page()
                .signin(email, new_password)
                .assert_page(False),

            DashboardPage(self)
                .assert_page(),
        )

    @register_test('test_forgot_password')
    def test_forgot_password(self):
        email, old_password = help_register(self)

        (
            DashboardPage(self)
                .assert_page(),

            SignedInHeaderPage(self)
                .logout(),

            SignoutPage(self)
                .assert_page()
                .signout(),

            SigninPage(self)
                .assert_page()
                .to_forgot_pass(),

            ForgotPasswordPage(self)
                .assert_page()
                .forgot_password(randemail(8))
                .assert_page()
                .forgot_password(email),

            PassResetDonePage(self)
                .assert_page()
            # .assert_heading()  # TODO doesn't work :(
        )


def help_register(self, email=None, password=None):
    if email is None:
        email = randemail(8)

    if password is None:
        password = randstr(8, numbers=True)

    (
        SignupPage(self).
            start()
            .assert_page()
            .signup(email, password)
            .assert_page(False)
    )

    return email, password