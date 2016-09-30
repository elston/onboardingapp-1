from ..tests import BaseTestCase

from ..page_objects.organization import OrganizationPage, CreateOrganizationPage
from ..page_objects.dashboard import DashboardPage
from ..page_objects.side_bar import SideBarPage

from ..tools import randstr, RegisterTest, register_test_case
from .test_register import help_register


@register_test_case('OrganizationTestCase')
class OrganizationTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_make_org',
        'test_make_many_orgs'
    )

    @register_test('test_make_org')
    def test_make_org(self):
        help_register(self)
        help_make_org(self)

    @register_test('test_make_many_orgs')
    def test_make_many_orgs(self):
        help_register(self)
        help_make_org(self)

        (
            OrganizationPage(self)
                .assert_page(),
            # .to_create_org(),  # TODO element selection issue :( better locator needed

            # CreateOrganizationPage(self)
            #     .assert_page(False),
        )


def help_make_org(self):
    (
        DashboardPage(self)
            .assert_page(),

        SideBarPage(self)
            .open()
            .to_organization(),

        OrganizationPage(self)
            .assert_page()
            .to_create_org(),

        CreateOrganizationPage(self)
            .assert_page()
            .add_org(randstr(5), randstr(60)),

        OrganizationPage(self)
            .assert_page()
    )
