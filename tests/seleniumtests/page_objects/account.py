from ..locators.account import AccountLocators, UpdateAccountLocators
from . import BasePageObject

from ..tools import chained_method


class AccountPage(BasePageObject):
    L = AccountLocators

    @chained_method
    def update_account(self):
        self.safe_find_element(self.L.update_account).click()
        return self


class UpdateAccountPage(BasePageObject):
    L = UpdateAccountLocators

    class Request(object):
        def __init__(self, level_number, limit_org_num=None,
                     limit_team_num=None, monthly_rate=None):

            self.level_number = str(level_number)
            self.limit_org_num = str(limit_org_num)
            self.limit_team_num = str(limit_team_num)
            self.monthly_rate = str(monthly_rate)

    def _get_account_level(self, level_number):
        by, locator = self.L.level_row
        locator %= level_number

        return self.safe_find_elements(by, locator)

    def check_account_level(self, request, check_type=True):
        if not isinstance(request, UpdateAccountPage.Request):
            raise TypeError('UpdateAccountPage.Request obj required')

        limit_raw = self._get_account_level(request.level_number)

        if not limit_raw:
            return not check_type

        if request.limit_org_num:
            if not filter(lambda x: x.text == request.limit_org_num, limit_raw):
                return not check_type

        if request.limit_team_num:
            if not filter(lambda x: x.text == request.limit_team_num, limit_raw):
                return not check_type

        if request.monthly_rate:
            if not filter(lambda x: request.monthly_rate in x.text, limit_raw):
                return not check_type

        return check_type

    @chained_method
    def assert_account_level(self, request, check_type=True):
        assert self.check_account_level(request, check_type=check_type)
        return self

    @chained_method
    def pay_with_card_for_level(self, level_number):
        by, locator = self.L.level_row_btn
        locator %= level_number

        self.safe_find_clickable_element((by, locator)).click()
        return self
