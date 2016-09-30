from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'accounts/logout/'
    TITLE = 'allstacks'

    singout_button = By.XPATH, "//button[text()='Sign Out']"
