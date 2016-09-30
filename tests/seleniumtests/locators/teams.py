from selenium.webdriver.common.by import By

from . import BaseLocators


class TeamsLocators(BaseLocators):
    URL = 'teams'
    TITLE = 'allstacks'

    to_create_team = By.XPATH, "//div[@id='addteam-div']//a[@onclick='check()']"
    teambox = By.ID, "teambox-title"


class CreateTeamsLocators(BaseLocators):
    STANDALONE = False

    team_org = By.ID, "id_organization"
    team_name = By.ID, "id_team_name"
    team_description = By.ID, "id_team_description"
    create_button = By.XPATH, "//input[@type='submit']"


class TeamsDetailsLocators(BaseLocators):
    CHECKER_URL = r'.*team/\d+$'
    TITLE = 'allstacks'

    add_member = By.XPATH, "//p[contains(@onclick, 'openbox(')]/i"
    members_heading = By.XPATH, "//h5[text()='MEMBERS']"
    members_list = By.ID, "members"  # TODO useful ?
    members_close_btn = By.XPATH, "//div[@id='close'][@onclick='closebox()']"

    add_service = By.XPATH, "//p[contains(@onclick, 'openbox2(')]/i"
    services_heading = By.XPATH, "//h5[text()='TOOLS']"
    services_list = By.ID, "services"  # TODO useful ?

    # to be formatted with the service
    service_image = By.XPATH, "//div[@id='tiles']//img[contains(@src, '%s')]"
    service_close = By.XPATH, "//div[div/img[contains(@src, '%s')]]//i"

    # services_img_list = By.XPATH, "//div[@id='tiles']//img"
