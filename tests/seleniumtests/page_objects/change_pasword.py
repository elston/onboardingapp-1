from ..locators.change_password import Locators
from ..page_objects import BasePageObject
from ..tools import chained_method


class ChangePasswordPage(BasePageObject):
    L = Locators

    @chained_method
    def change_password(self, old_pass, new_pass):
        elem = self.safe_find_element(self.L.oldpass)
        elem.clear()
        elem.send_keys(old_pass)

        elem = self.safe_find_element(self.L.newpass1)
        elem.clear()
        elem.send_keys(new_pass)

        elem = self.safe_find_element(self.L.newpass2)
        elem.clear()
        elem.send_keys(new_pass)

        self.safe_find_element(self.L.button).click()

        return self
