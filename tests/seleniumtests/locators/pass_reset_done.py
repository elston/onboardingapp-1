from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'accounts/password/reset/done/'
    TITLE = 'allstacks'

    heading = By.XPATH, "//h2[text()='Password Reset']"
