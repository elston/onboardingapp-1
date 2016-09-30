from selenium import webdriver

from ..settings import CHROMEDRIVER_PATH, DRIVER, FULL_SCREEN, TEST_ON_PRODUCTION

if TEST_ON_PRODUCTION:
    # don't run LiveServer when testing on production server
    from django.test import TestCase as TestCase
else:
    from django.contrib.staticfiles.testing import StaticLiveServerTestCase as TestCase


class BaseTestCase(TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()

        if DRIVER == 'firefox':
            self.driver = webdriver.Firefox()
        elif DRIVER == 'chrome':
            self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
        else:
            raise AttributeError('driver not specified')

        if FULL_SCREEN:
            self.driver.maximize_window()

    def tearDown(self):
        self.driver.close()

        super(BaseTestCase, self).tearDown()
