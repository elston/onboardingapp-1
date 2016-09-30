from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'accounts/login/'
    TITLE = 'allstacks'

    email = By.ID, "id_login"
    password = By.ID, "id_password"
    button = By.XPATH, "//input[@value='Sign in!']"

    to_forgot_pass = By.XPATH, "//a[text()='Forgot Password?']"
