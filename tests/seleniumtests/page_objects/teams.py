from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..locators.teams import TeamsLocators, CreateTeamsLocators, TeamsDetailsLocators
from . import BasePageObject

from ..tools import chained_method
from ..settings import WAIT_PERIOD_SHORT, WAIT_PERIOD_JOTA


class TeamsPage(BasePageObject):
    L = TeamsLocators

    @chained_method
    def to_create_team(self):
        self.safe_find_element(self.L.to_create_team).click()
        return self

    @chained_method
    def access_teambox(self, err_cb=None):
        elem = self.safe_find_element(self.L.teambox)
        if elem.is_enabled():
            elem.click()
        else:
            if err_cb:
                err_cb()
        return self


class CreateTeamsPage(BasePageObject):
    L = CreateTeamsLocators

    @chained_method
    def add_team(self, team_name, description, org_name=None):

        team_org = self.safe_find_element(self.L.team_org)
        # No org exists
        if team_org.tag_name == 'input':
            team_org.clear()
            team_org.send_keys(org_name)
        elif team_org.tag_name == 'select':
            pass
        else:
            print 'Dragons be here. Unexpected tag for CreateTeamsPage.team_org element'

        elem = self.safe_find_element(self.L.team_name)
        if not elem.is_displayed():
            raise AssertionError('Failed to create a team. Possibly limit is reached')
        elem.clear()
        elem.send_keys(team_name)

        elem = self.safe_find_element(self.L.team_description)
        elem.clear()
        elem.send_keys(description)

        self.safe_find_element(self.L.create_button).click()
        return self


class TeamsDetailsPage(BasePageObject):
    L = TeamsDetailsLocators

    def check_page(self, check_type=True):
        if not super(TeamsDetailsPage, self).check_page(check_type):
            return False

        if not self.D.find_elements(*self.L.members_heading):
            return False

        if not self.D.find_elements(*self.L.services_heading):
            return False

        return True

    @chained_method
    def add_member(self):
        self.safe_find_element(self.L.add_member).click()
        return self

    @chained_method
    def to_add_service(self):
        self.safe_find_element(self.L.add_service).click()
        return self

    @chained_method
    def remove_added_service(self, service):
        by, locator = self.L.service_close
        self.D.find_element(by, locator % service).click()

        try:
            # http://stackoverflow.com/questions/19003003/check-if-any-alert-exists-using-selenium-with-python
            WebDriverWait(self.D, WAIT_PERIOD_SHORT).until(EC.alert_is_present(),
                                           'Timed out waiting for PA creation '
                                           'confirmation popup to appear.')

            self.D.switch_to_alert().accept()
            print "alert accepted"

        except TimeoutException:
            print "no alert"

        # removal processing causes delay. needs page assertion on return
        self.assert_page()

        return self

    @chained_method
    def assert_service_is_added(self, service, check_type=True):
        assert self.check_service_is_added(service, check_type)
        return self

    def check_service_is_added(self, service, check_type=True):
        by, locator = self.L.service_image
        locator %= service

        # old elements get cleaned with delay. causes false positive result,
        # TODO effectively the same as sleep :( possibly other validation would be handy ??
        if not check_type:
            try:
                WebDriverWait(self.D, WAIT_PERIOD_JOTA).until(
                    EC.invisibility_of_element_located((by, locator))
                )
            except TimeoutException as e:
                return not check_type

        if self.D.find_elements(by, locator):

            return check_type

        return not check_type
