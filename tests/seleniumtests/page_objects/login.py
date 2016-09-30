from . import BasePageObject
from ..locators.signin import Locators

from ..tools import chained_method


class SigninPage(BasePageObject):
    L = Locators

    @chained_method
    def login(self, email, password):
        elem = self.safe_find_element(self.L.email)
        elem.clear()
        elem.send_keys(email)

        elem = self.safe_find_element(self.L.password1)
        elem.clear()
        elem.send_keys(password)

        self.safe_find_element(self.L.button).click()

        return self
