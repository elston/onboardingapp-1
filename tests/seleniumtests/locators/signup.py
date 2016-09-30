from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'accounts/signup/?'
    TITLE = 'allstacks'

    email = By.ID, "id_email"
    password1 = By.ID, "id_password1"
    password2 = By.ID, "id_password2"
    button = By.XPATH, "//input[@value='Get Started']"
