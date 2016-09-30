from ..locators.service_mailinator import Locators
from ..page_objects import BasePageObject
from ..tools import chained_method


class MailinatorHomePage(BasePageObject):
    L = Locators

    @chained_method
    def access_inbox(self, email):
        elem = self.safe_find_element(self.L.email)
        elem.clear()
        elem.send_keys(email)

        self.safe_find_element(self.L.button).click()

        return self
