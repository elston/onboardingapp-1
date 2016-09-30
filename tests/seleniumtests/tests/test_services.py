from ..tests import BaseTestCase
from ..tools import hush, RegisterTest, register_test_case

from ..page_objects.services import *
from ..page_objects.teams import TeamsDetailsPage, TeamsPage
from ..page_objects.side_bar import SideBarPage
from ..page_objects.dashboard import DashboardPage
from ..page_objects.signin import SigninPage

from .test_register import help_register
from .test_teams import help_make_team

email = "allstacksdemo@gmail.com"
pwd = "Test1111"
team_name = "TeamName"
org_name = "OrgName"


@register_test_case('ServicesTestCase')
class ServicesTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_asana',
        'test_bitbucket',
        # 'test_box'  # TODO redirects to own site # coming soon
        # 'test_dropbox', # TODO redirects to own site # coming soon
        # 'test_github'  # TODO no token
        # 'test_hipchat',  # TODO does it really work on manual testing
        # 'test_jira',  # TODO infinitely loads !?
        # 'test_quay',  # TODO no token
        # 'test_slack',  # TODO no token
        # 'test_toggle',  # TODO no token & workspace
        # 'test_trello',  # TODO no token
        # 'test_zendesk',  # TODO no token
    )

    @register_test('test_asana')
    def test_asana(self):
        self.help_test_add_and_remove_service(
            AsanaPage,
            token="0/862fe1b3e0c2d6b82b919a74abf452a6",
            workspace="Allstack",
        )

    @register_test('test_bitbucket')
    def test_bitbucket(self):
        self.help_test_add_and_remove_service(
            BitbucketPage,
            password="Testing88",
            group_name="OrgName",
        )

    @register_test('test_box')
    def test_box(self):
        self.help_test_add_and_remove_service(
            BoxPage,
        )

    @register_test('test_dropbox')
    def test_dropbox(self):
        self.help_test_add_and_remove_service(
            DropboxPage,
        )

    @register_test('test_github')
    def test_github(self):
        self.help_test_add_and_remove_service(
            GithubPage,
            token=None,
            org_name="AllstackOrg",
            team_name="AllstackTeam"
        )

    @register_test('test_hipchat')
    def test_hipchat(self):
        self.help_test_add_and_remove_service(
            HipchatPage,
            token="Hw6JNtPde9LR46QfyGsrprColI9v9AI9T6QkJRIb",
            room_name="allstacks.hipchat.com",
        )

    @register_test('test_jira')
    def test_jira(self):
        self.help_test_add_and_remove_service(
            JiraPage,
            site_name="allstacks.atlassian.net",
            password="Testing88",
        )

    @register_test('test_quay')
    def test_quay(self):
        self.help_test_add_and_remove_service(
            QuayPage,
            token=None,
            organization=org_name,  # supposedly
            team_name=team_name,  # supposedly
        )

    @register_test('test_slack')
    def test_slack(self):
        self.help_test_add_and_remove_service(
            SlackPage,
            token=None,
        )

    @register_test('test_toggle')
    def test_toggle(self):
        self.help_test_add_and_remove_service(
            TogglPage,
            token=None,
            workspace=None,
        )

    @register_test('test_trello')
    def test_trello(self):
        self.help_test_add_and_remove_service(
            TrelloPage,
            key="4e9c4c1e6557eb277daa286f54558582",
            token=None,
            team_name="AllStackDemo"
        )

    @register_test('test_zendesk')
    def test_zendesk(self):
        self.help_test_add_and_remove_service(
            ZenDeskPage,
            token=None,
            subdomain="https://allstacks.zendesk.com"
        )

    def help_test_add_and_remove_service(self, service_cls, **params):
        help_navigate_to_services(self)

        teams_details_page = TeamsDetailsPage(self)
        service_page = service_cls(self)

        if [
            teams_details_page
                    .assert_page()
                    .check_service_is_added(service_cls.L.NAME)
        ].pop():
            (
                teams_details_page
                    .remove_added_service(service_cls.L.NAME)
                    .assert_service_is_added(service_cls.L.NAME, False)
            )

        (
            teams_details_page
                .to_add_service(),

            service_page
                .assert_page()
                .select_service()
                .add_tool(**params),

            teams_details_page
                .assert_page()
                .assert_service_is_added(service_cls.L.NAME)
                .remove_added_service(service_cls.L.NAME)
                .assert_service_is_added(service_cls.L.NAME, False),
        )


def help_navigate_to_services(self):
    (
        SigninPage(self)
            .start()
            .assert_page()
            .signin(email, pwd)
            .check_page_cb(ok_cb=lambda: help_register(self, email, pwd)),

        DashboardPage(self)
            .assert_page(),

        hush(lambda: help_make_team(self, team_name, 'TeamDesc', org_name), AssertionError),

        SideBarPage(self)
            .open()
            .assert_page()
            .to_teams(),

        TeamsPage(self)
            .assert_page()
            .access_teambox(),

        TeamsDetailsPage(self)
            .assert_page()
    )