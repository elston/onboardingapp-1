from ..tools import randstr, randemail, RegisterTest, register_test_case
from ..tests import BaseTestCase

from ..page_objects.team_members import TeamMembersPage
from ..page_objects.teams import TeamsDetailsPage

from .test_register import help_register
from .test_teams import help_make_team


@register_test_case('MembersTestCase')
class MembersTestCase(BaseTestCase):

    register_test = RegisterTest(
        'test_invite_member',
        'test_invite_multiple_members'
    )

    @register_test('test_invite_member')
    def test_invite_member(self):
        help_register(self)
        help_make_team(self)
        help_invite_member(self)

    @register_test('test_invite_multiple_members')
    def test_invite_multiple_members(self):
        help_register(self)
        help_make_team(self)

        for _ in range(3):
            help_invite_member(self)


def help_invite_member(self):
    (
        TeamsDetailsPage(self)
            .assert_page()
            .add_member(),

        TeamMembersPage(self)
            .invite_member(randstr(8), randstr(8), randemail(8))
    )
