from ..page_objects import BasePageObject
from ..locators.dashboard import Locators

from ..tools import chained_method


class DashboardPage(BasePageObject):
    L = Locators

    @chained_method
    def logout(self):
        self.safe_find_element(self.L.logout).click()
        return self
