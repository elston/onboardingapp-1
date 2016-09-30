from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    STANDALONE = False

    # affects visibility
    toggling_wrapper = By.ID, "wrapper"

    to_dashboard = By.XPATH, "//a[@href='/dashboard']"

    to_teams = By.XPATH, "//a[@href='/teams']"
    to_organization = By.XPATH, "//a[@href='/organization/']"
    to_profile = By.XPATH, "//a[@href='/user/plan']"

    to_settings = By.XPATH, "//a[@href='/accounts/password/change/']"
    logout = By.XPATH, "//li/a[text()='Logout']"
