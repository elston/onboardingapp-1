from ..locators.pass_reset_done import Locators
from ..page_objects import BasePageObject
from ..tools import chained_method


class PassResetDonePage(BasePageObject):
    L = Locators

    @chained_method
    def assert_page(self, assert_true=True):
        if len(self.D.find_elements(*self.L.heading)) == 0:
            raise AssertionError

        return self
