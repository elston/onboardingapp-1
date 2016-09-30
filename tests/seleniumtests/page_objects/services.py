from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..locators.services import *
from . import BasePageObject

from ..tools import chained_method
from ..settings import WAIT_PERIOD_LONG


class ServicesPage(BasePageObject):
    L = None

    @chained_method
    def select_service(self):
        self.safe_find_element(self.L.SERVICE_BOX).click()
        return self

    @chained_method
    def add_tool(self, *args, **kwargs):
        self.safe_find_element(self.L.ADD_TOOL).click()
        return self

    @chained_method
    def close_page(self):
        self.safe_find_element(self.L.services_close_btn).click()
        return self

    def check_page(self, check_type=True):
        if not isinstance(check_type, bool):
            raise TypeError("'check_type' must be boolean")

        # wait until bg elements become accessible
        try:
            WebDriverWait(self.D, WAIT_PERIOD_LONG).until_not(
                EC.invisibility_of_element_located(self.L.__shadowing__)
            )
        except TimeoutException as e:
            return not check_type

        shadowing = self.safe_find_element(self.L.__shadowing__).get_attribute('style')
        return ('block' in shadowing and self.check_url()) == check_type


class AsanaPage(ServicesPage):
    L = AsanaLocators

    @chained_method
    def add_tool(self, token, workspace):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.workspace)
        elem.clear()
        elem.send_keys(workspace)

        return ServicesPage.add_tool(self)


class BitbucketPage(ServicesPage):
    L = BitbucketLocators

    @chained_method
    def add_tool(self, password, group_name):
        elem = self.safe_find_element(self.L.password)
        elem.clear()
        elem.send_keys(password)

        elem = self.safe_find_element(self.L.group_name)
        elem.clear()
        elem.send_keys(group_name)

        return ServicesPage.add_tool(self)


class BoxPage(ServicesPage):
    L = BoxLocators


class DropboxPage(ServicesPage):
    L = DropboxLocators


class GithubPage(ServicesPage):
    L = GithubLocators

    @chained_method
    def add_tool(self, token, org_name, team_name):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.org_name)
        elem.clear()
        elem.send_keys(org_name)

        elem = self.safe_find_element(self.L.team_name)
        elem.clear()
        elem.send_keys(team_name)

        return ServicesPage.add_tool(self)


class HipchatPage(ServicesPage):
    L = HipchatLocators

    @chained_method
    def add_tool(self, token, room_name):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.room_name)
        elem.clear()
        elem.send_keys(room_name)

        return ServicesPage.add_tool(self)


class JiraPage(ServicesPage):
    L = JiraLocators

    @chained_method
    def add_tool(self, site_name, password):
        elem = self.safe_find_element(self.L.site_name)
        elem.clear()
        elem.send_keys(site_name)

        elem = self.safe_find_element(self.L.password)
        elem.clear()
        elem.send_keys(password)

        return ServicesPage.add_tool(self)


class QuayPage(ServicesPage):
    L = QuayLocators

    @chained_method
    def add_tool(self, token, organization, team_name):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.organization)
        elem.clear()
        elem.send_keys(organization)

        elem = self.safe_find_element(self.L.team_name)
        elem.clear()
        elem.send_keys(team_name)

        return ServicesPage.add_tool(self)


class SlackPage(ServicesPage):
    L = SlackLocators

    @chained_method
    def add_tool(self, token):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        return ServicesPage.add_tool(self)


class TogglPage(ServicesPage):
    L = TogglLocators

    @chained_method
    def add_tool(self, token, workspace):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.workspace)
        elem.clear()
        elem.send_keys(workspace)

        return ServicesPage.add_tool(self)


class TrelloPage(ServicesPage):
    L = TrelloLocators

    @chained_method
    def add_tool(self, key, token, team_name):
        elem = self.safe_find_element(self.L.key)
        elem.clear()
        elem.send_keys(key)

        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.team_name)
        elem.clear()
        elem.send_keys(team_name)


class ZenDeskPage(ServicesPage):
    L = ZendeskLocators

    @chained_method
    def add_tool(self, token, subdomain):
        elem = self.safe_find_element(self.L.token)
        elem.clear()
        elem.send_keys(token)

        elem = self.safe_find_element(self.L.subdomain)
        elem.clear()
        elem.send_keys(subdomain)

        return ServicesPage.add_tool(self)
