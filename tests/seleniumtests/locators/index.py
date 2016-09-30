from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = ''
    TITLE = 'alltacks'

    enter_email = By.XPATH, "//form[@action='/accounts/signup/']//input[@type='text']"
    sign_me_up = By.XPATH, "//form[@action='/accounts/signup/']//input[@type='submit']"
