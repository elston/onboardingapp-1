from selenium.webdriver.common.by import By

from . import BaseLocators


class BaseServiceLocators(BaseLocators):
    STANDALONE = False
    CHECKER_URL = r'.*team/\d+$'

    NAME = None
    SERVICE_BOX = None
    ADD_TOOL = By.XPATH, "//input[@type='submit'][@value='Add Tool']"
    PARAMS = []

    By.XPATH, "//div[input[@type='submit'][@value='Add Tool']]/*"
    services_close_btn = By.XPATH, "//div[@id='close'][@onclick='closebox2()']"


class AsanaLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "asanaBox"
    NAME = "asana"

    token = By.ID, "id_token"
    workspace = By.ID, "id_workspace"

    PARAMS = [token, workspace]


class BitbucketLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "bitbucketBox"
    NAME = 'bitbucket'

    password = By.ID, "id_password"
    group_name = By.ID, "id_group_name"

    PARAMS = [password, group_name]


class BoxLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "boxBox"
    NAME = 'box'


class DropboxLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "dropboxBox"
    NAME = 'dropbox'


class GithubLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "githubBox"
    NAME = 'github'

    token = By.ID, "id_token"
    org_name = By.ID, "id_org_name"
    team_name = By.ID, "id_team_name"

    PARAMS = [token, org_name, team_name]


class HipchatLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "hipchatBox"
    NAME = "hipchat"

    token = By.ID, "id_token"
    room_name = By.ID, "id_org_name"

    PARAMS = [token, room_name]


class JiraLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "jiraBox"
    NAME = "jira"

    site_name = By.ID, "id_sitename"
    password = By.ID, "id_password"

    PARAMS = [site_name, password]


class QuayLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "quayBox"
    NAME = "quay"

    token = By.ID, "id_token"
    organization = By.ID, "id_organization"
    team_name = By.ID, "id_team"

    PARAMS = [token, organization, team_name]


class SlackLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "slackBox"
    NAME = "slack"

    token = By.ID, "id_team_token"

    PARAMS = [token]


class TogglLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "togglBox"
    NAME = 'toggl'

    token = By.ID, "id_token"
    workspace = By.ID, "id_workspace"

    PARAMS = [token, workspace]


class TrelloLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "trelloBox"
    NAME = "trello"

    key = By.ID, "id_key"
    token = By.ID, "id_token"
    team_name = By.ID, "id_team_name"

    PARAMS = [key, token, team_name]


class ZendeskLocators(BaseServiceLocators):
    SERVICE_BOX = By.ID, "zendeskBox"
    NAME = "zendesk"

    token = By.ID, "id_token"
    subdomain = By.ID, "id_subdomain"

    PARAMS = [token, subdomain]
