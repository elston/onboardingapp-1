from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'accounts/password/reset/'
    TITLE = 'allstacks'

    email = By.ID, "id_email"
    button = By.XPATH, "//input[contains(@value, 'Reset Password')]"
