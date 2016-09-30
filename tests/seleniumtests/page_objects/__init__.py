import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..tools import chained_method
from ..settings import SITE, WAIT_PERIOD_MIDDLE, WAIT_PERIOD_SHORT, TEST_ON_PRODUCTION


class BasePageObject(object):
    L = None

    def __init__(self, test_env):

        if self.L is None:
            raise NotImplementedError('Locators not provided')

        self.test_env = test_env
        self.D = test_env.driver

    # ----- page navigation means -----

    @chained_method
    def start(self):

        self._is_standalone("Can't start. ")

        if self.L.URL is None:
            raise NotImplementedError('Missing url')

        self.D.get(
            self.L.URL if self.L.URL.startswith('http') else '/'.join(
                [SITE if TEST_ON_PRODUCTION else self.test_env.live_server_url, self.L.URL])
        )
        return self

    @chained_method
    def go_forward(self):
        self.D.forward()
        return self

    @chained_method
    def go_back(self):
        self.D.back()
        return self

    # ----- page validation means -----

    # plz don't override this method, consider check_page instead
    @chained_method
    def assert_page(self, check_type=True):

        assert self.check_page(check_type)
        return self

    # plz don't override this method, consider check_page instead
    @chained_method
    def check_page_cb(self, check_type=True, ok_cb=None, err_cb=None):

        if self.check_page(check_type):
            if ok_cb:
                ok_cb()
        else:
            if err_cb:
                err_cb()

        return self

    def check_page(self, check_type=True):

        if not isinstance(check_type, bool):
            raise TypeError("'check_type' must be boolean")

        self._is_standalone("plz override for custom assertion")

        # wait until bg elements become accessible
        try:
            WebDriverWait(self.D, WAIT_PERIOD_MIDDLE).until(
                EC.invisibility_of_element_located(self.L.__shadowing__)
            )
        except TimeoutException:
            return not check_type

        # assert self.check_title() == check_type
        return self.check_url() == check_type

    def check_url(self):

        if self.L.CHECKER_URL is None and self.L.URL is None:
            raise NotImplementedError('Missing url for checking')

        if self.L.CHECKER_URL is not None:
            if re.match(self.L.CHECKER_URL, self.D.current_url):
                return True

        if self.L.URL is not None:
            if self.L.URL in self.D.current_url:
                return True

        return False

    def check_title(self):
        if not self.L.TITLE:
            raise NotImplementedError('Missing title')

        return self.L.TITLE.lower() in self.D.title.lower()

    def _is_standalone(self, message):
        if not self.L.STANDALONE:
            raise NotImplementedError("Not a standalone page '%s'. %s" % (self.__class__.__name__, message))

    # ----- element handling means -----

    def safe_find_element(self, params):
        try:
            element = WebDriverWait(self.D, WAIT_PERIOD_SHORT).until(
                EC.presence_of_element_located(params)
            )
            return element
        except TimeoutException as e:
            raise AssertionError(e)

    def safe_find_clickable_element(self, params):
        try:
            element = WebDriverWait(self.D, WAIT_PERIOD_SHORT).until(
                EC.element_to_be_clickable(params)
            )
            return element
        except TimeoutException as e:
            raise AssertionError(e)

    def safe_find_elements(self, *params):
        # wait until bg elements become accessible
        try:
            elements = WebDriverWait(self.D, WAIT_PERIOD_SHORT).until(
                EC.presence_of_all_elements_located(params)
            )
            return elements
        except TimeoutException as e:
            return []
