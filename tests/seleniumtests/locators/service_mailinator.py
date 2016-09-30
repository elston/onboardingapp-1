from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    URL = 'https://www.mailinator.com/'
    TITLE = 'mailinator'

    email = By.ID, "inboxfield"
    button = By.XPATH, "//button[contains(text(), 'Go!')]"
