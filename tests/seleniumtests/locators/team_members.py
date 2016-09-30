from selenium.webdriver.common.by import By

from . import BaseLocators


class Locators(BaseLocators):
    STANDALONE = False

    first_name = By.ID, "id_first_name"
    last_name = By.ID, "id_last_name"
    user_email = By.ID, "id_user_email"
    invite_button = By.XPATH, "//input[@type='submit'][@value='Invite']"

    admin_checkbox = By.ID, "checkbox2"
