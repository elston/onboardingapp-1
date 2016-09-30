from selenium.webdriver.common.keys import Keys

from . import BasePageObject
from ..locators.index import Locators

from ..tools import chained_method


class IndexPage(BasePageObject):
    L = Locators

    @chained_method
    def signup(self, email):
        assert self.check_title()

        elem = self.safe_find_element(self.L.enter_email)
        elem.clear()
        elem.send_keys(email)
        elem.send_keys(Keys.RETURN)

        return self
