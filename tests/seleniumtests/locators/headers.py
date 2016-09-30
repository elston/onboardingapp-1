from selenium.webdriver.common.by import By

from . import BaseLocators


class SignedInHeaderLocators(BaseLocators):
    STANDALONE = False

    menu_toggle = By.ID, "menu-toggle"
    logout = By.XPATH, "//div/a[text()='Logout']"


class SignedOutHeaderLocators(BaseLocators):
    STANDALONE = False
