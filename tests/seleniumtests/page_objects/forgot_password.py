from ..page_objects import BasePageObject
from ..locators.forgot_password import Locators

from ..tools import chained_method


class ForgotPasswordPage(BasePageObject):
    L = Locators

    @chained_method
    def forgot_password(self, email):
        elem = self.safe_find_element(self.L.email)
        elem.clear()
        elem.send_keys(email)

        self.safe_find_element(self.L.button).click()

        return self
