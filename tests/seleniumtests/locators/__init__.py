from selenium.webdriver.common.by import By


class BaseLocators(object):
    URL = None
    CHECKER_URL = None
    TITLE = None
    STANDALONE = True

    # blocks bg elements from being accessed
    # needs to be waited until it disappears
    __shadowing__ = By.ID, "shadowing"
