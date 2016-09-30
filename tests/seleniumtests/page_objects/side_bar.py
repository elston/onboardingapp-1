from ..page_objects import BasePageObject
from ..locators.side_bar import Locators
from headers import SignedInHeaderPage

from ..tools import chained_method

from time import sleep
from ..settings import WAIT_PERIOD_JOTA


class SideBarPage(BasePageObject):
    L = Locators

    def check_page(self, check_type=True):
        if not isinstance(check_type, bool):
            raise TypeError("'check_type' must be boolean")

        shadowing = self.safe_find_element(self.L.toggling_wrapper).get_attribute('class')
        return ('toggled' not in shadowing) == check_type

    @chained_method
    def open(self):
        self.check_page_cb(err_cb=lambda: SignedInHeaderPage(self.test_env).assert_page().toggle_side_bar())
        return self

    @chained_method
    def close(self):
        self.check_page_cb(ok_cb=lambda: SignedInHeaderPage(self.test_env).assert_page().toggle_side_bar())
        return self

    @chained_method
    def to_dashboard(self):
        self.safe_find_element(self.L.to_dashboard).click()
        return self

    @chained_method
    def to_teams(self):

        sleep(WAIT_PERIOD_JOTA)  # TODO terrible, checking out toasts could help
        self.safe_find_clickable_element(self.L.to_teams).click()
        return self

    @chained_method
    def to_organization(self):
        self.safe_find_element(self.L.to_organization).click()
        return self

    @chained_method
    def to_profile(self):
        self.safe_find_element(self.L.to_profile).click()
        return self

    @chained_method
    def to_settings(self):
        self.safe_find_element(self.L.to_settings).click()
        return self

    @chained_method
    def logout(self):
        self.safe_find_element(self.L.logout).click()
        return self
