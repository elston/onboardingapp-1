from ..locators.signin import Locators
from . import BasePageObject

from ..tools import chained_method


class SigninPage(BasePageObject):
    L = Locators

    @chained_method
    def signin(self, email, password):
        elem = self.safe_find_element(self.L.email)
        elem.clear()
        elem.send_keys(email)

        elem = self.safe_find_element(self.L.password)
        elem.clear()
        elem.send_keys(password)

        self.safe_find_element(self.L.button).click()

        return self

    @chained_method
    def to_forgot_pass(self):
        self.safe_find_element(self.L.to_forgot_pass).click()

        return self
