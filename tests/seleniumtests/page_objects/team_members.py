from . import BasePageObject
from ..locators.team_members import Locators

from ..tools import chained_method


class TeamMembersPage(BasePageObject):
    L = Locators

    @chained_method
    def invite_member(self, first_name, last_name, email, admin=False):
        elem = self.safe_find_element(self.L.first_name)
        elem.clear()
        elem.send_keys(first_name)

        elem = self.safe_find_element(self.L.last_name)
        elem.clear()
        elem.send_keys(last_name)

        elem = self.safe_find_element(self.L.user_email)
        elem.clear()
        elem.send_keys(email)

        if admin:
            self.safe_find_element(self.L.admin_checkbox)

        self.safe_find_element(self.L.invite_button).click()

        return self
