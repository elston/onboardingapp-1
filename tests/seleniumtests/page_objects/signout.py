from ..locators.signout import Locators
from ..page_objects import BasePageObject
from ..tools import chained_method


class SignoutPage(BasePageObject):
    L = Locators

    @chained_method
    def signout(self):
        self.safe_find_element(self.L.singout_button).click()

        return self
