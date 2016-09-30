from selenium.webdriver.common.by import By

from . import BaseLocators


class AccountLocators(BaseLocators):
    URL = 'user/plan'
    TITLE = 'allstacks'

    update_account = By.XPATH, "//a[@href='/user/account/update']"


class UpdateAccountLocators(BaseLocators):
    URL = 'user/account/update'
    TITLE = 'allstacks'

    # to be formatted with the level number
    level_row = By.XPATH, "//tr[td[text()='Level %s']]//td"
    level_row_btn = By.XPATH, "//tr[td[text()='Level %s']]//button"
