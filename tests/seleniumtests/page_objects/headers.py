from ..page_objects import BasePageObject
from ..locators.headers import SignedInHeaderLocators, SignedOutHeaderLocators

from ..tools import chained_method


class SignedInHeaderPage(BasePageObject):
    L = SignedInHeaderLocators

    @chained_method
    def logout(self):
        self.safe_find_element(self.L.logout).click()
        return self

    @chained_method
    def toggle_side_bar(self):
        self.safe_find_element(self.L.menu_toggle).click()
        return self


class SignedOutHeaderPage(BasePageObject):
    L = SignedOutHeaderLocators
