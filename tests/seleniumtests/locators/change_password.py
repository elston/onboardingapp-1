from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'accounts/password/change/'
    TITLE = 'allstacks'

    oldpass = By.XPATH, "//input[@id='id_oldpassword']"
    newpass1 = By.XPATH, "//input[@id='id_password1']"
    newpass2 = By.XPATH, "//input[@id='id_password2']"
    button = By.XPATH, "//input[contains(@value, 'Change Password')]"
