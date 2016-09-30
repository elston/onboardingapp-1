from ..tools import RegisterTest, register_test_case
from ..tests import BaseTestCase

from ..page_objects.account import AccountPage, UpdateAccountPage
from ..page_objects.dashboard import DashboardPage
from ..page_objects.side_bar import SideBarPage

from .test_register import help_register


@register_test_case('AccountTestCase')
class AccountTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_update_account_level_1',
        'test_update_account_level_2',
        'test_update_account_level_3',
    )

    def help_test_update_account_level_N(self, request):

        (
            help_register(self),

            DashboardPage(self)
                .assert_page(),

            help_navigate_to_update_account(self),

            UpdateAccountPage(self)
                .assert_page()
                .assert_account_level(request)
                .pay_with_card_for_level(request.level_number)
            # TODO bg invisibility assertion needed (__shadowing__ is missing)
            # TODO can't catch the payments context menu. iframe?
        )

    @register_test('test_update_account_level_1')
    def test_update_account_level_1(self):
        self.help_test_update_account_level_N(UpdateAccountPage.Request(1, 2, 5, 23))

    @register_test('test_update_account_level_2')
    def test_update_account_level_2(self):
        self.help_test_update_account_level_N(UpdateAccountPage.Request(2, 4, 10, 47))

    @register_test('test_update_account_level_3')
    def test_update_account_level_3(self):
        self.help_test_update_account_level_N(UpdateAccountPage.Request(3, 100, 10000, 99))


def help_navigate_to_update_account(self):

    (
        SideBarPage(self)
            .open()
            .assert_page()
            .to_profile(),

        AccountPage(self)
            .assert_page()
            .update_account(),
    )
