from ..tools import randstr, RegisterTest, register_test_case
from . import BaseTestCase

from ..page_objects.dashboard import DashboardPage
from ..page_objects.side_bar import SideBarPage
from ..page_objects.teams import CreateTeamsPage, TeamsPage

from .test_register import help_register
from .test_organization import help_make_org


@register_test_case('TeamsTestCase')
class TeamsTestCase(BaseTestCase):

    register_test = RegisterTest(
        "test_create_team_from_scratch",
        "test_create_team_with_existing_org",
    )

    @register_test('test_create_team_from_scratch')
    def test_create_team_from_scratch(self):
        help_register(self)
        help_make_team(self)

    @register_test('test_create_team_with_existing_org')
    def test_create_team_with_existing_org(self):
        help_register(self)
        help_make_org(self)

        (
            SideBarPage(self)
                .to_dashboard(),

            DashboardPage(self)
                .assert_page(),
        )

        help_make_team(self)


def help_make_team(self, team_name=None, description=None, org_name=None):
    if not team_name:
        team_name = randstr(8)

    if not description:
        description = randstr(8)

    if not org_name:
        org_name = randstr(8)

    (
        DashboardPage(self)
            .assert_page(),

        SideBarPage(self)
            .open()
            .assert_page()
            .to_teams(),

        TeamsPage(self)
            .assert_page()
            .to_create_team(),

        CreateTeamsPage(self)
            .add_team(team_name, description, org_name),
    )
