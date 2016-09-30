from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..locators.organization import OrgLocators, CreateOrgLocators
from . import BasePageObject

from ..tools import chained_method
from ..settings import WAIT_PERIOD_SHORT


class OrganizationPage(BasePageObject):
    L = OrgLocators

    @chained_method
    def to_create_org(self):
        elem = WebDriverWait(self.D, WAIT_PERIOD_SHORT).until(
            EC.element_to_be_clickable(self.L.to_create_org)
        )
        if elem:
            elem.click()
        return self


class CreateOrganizationPage(BasePageObject):
    L = CreateOrgLocators

    def check_page(self, check_type=True):

        if not isinstance(check_type, bool):
            raise TypeError("'check_type' must be boolean")

        state = self.D.find_elements(*self.L.widget_state)
        if state:
            if ('block' not in state.pop().get_attribute('style')) == check_type:
                return False
        else:
            if check_type:
                return False

        return True

    @chained_method
    def add_org(self, name, description):

        elem = self.safe_find_element(self.L.org_name)
        elem.clear()
        elem.send_keys(name)

        elem = self.safe_find_element(self.L.description)
        elem.clear()
        elem.send_keys(description)
        self.safe_find_element(self.L.create_button).click()

        return self
