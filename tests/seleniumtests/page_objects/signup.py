from ..locators.signup import Locators
from ..page_objects import BasePageObject

from ..tools import chained_method


class SignupPage(BasePageObject):
    L = Locators

    @chained_method
    def signup(self, email, password):
        elem = self.safe_find_element(self.L.email)
        elem.clear()
        elem.send_keys(email)

        elem = self.safe_find_element(self.L.password1)
        elem.clear()
        elem.send_keys(password)

        elem = self.safe_find_element(self.L.password2)
        elem.clear()
        elem.send_keys(password)

        self.safe_find_element(self.L.button).click()

        return self
