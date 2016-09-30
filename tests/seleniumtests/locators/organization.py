from selenium.webdriver.common.by import By

from . import BaseLocators


class OrgLocators(BaseLocators):
    URL = 'organization/'
    TITLE = 'allstacks'

    to_create_org = By.XPATH, "//div[@id='add-organization']//a[@onclick='check()']"


class CreateOrgLocators(BaseLocators):
    STANDALONE = False

    widget_state = By.ID, "box2"

    # heading = "//h1[text()='Create Organization']"
    org_name = By.ID, "id_name"
    description = By.ID, "id_description"
    create_button = By.XPATH, "//input[@type='submit'][@value='Create']"
