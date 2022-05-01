import os
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException

from checker.controllers.resources.exceptions import ElementNotFoundException
from checker.controllers.resources.expected_conditions import AnyElementWithLocatorsVisible


class RobotDriver:
    __element_timeout = 10
    __driver_options = Options()
    __driver_options.headless = True

    __driver_options.binary_location = os.getenv("FIREFOX_PATH", default="")
    try:
        driver = webdriver.Firefox(executable_path=os.getenv("WEBDRIVER_PATH", default=""), options=__driver_options)
    except WebDriverException:
        driver = None

    def get_element(self,
                    element_locator,
                    timeout: int = 0,
                    dynamic_element: bool = False,
                    multiple_elements: bool = False) -> Optional[WebElement]:

        if not timeout:
            timeout = self.__element_timeout

        try:
            if dynamic_element:
                return element_locator
            else:
                return WebDriverWait(self.driver, timeout).until(
                    AnyElementWithLocatorsVisible(element_locator, multiple_elements)
                )
        except (TimeoutException, WebDriverException):
            return None

    def get_dynamic_element(self,
                            element,
                            *dynamic_value,
                            timeout: int = 0,
                            multiple_elements: bool = False) -> Optional[WebElement]:
        by_type, locator = element
        locator = locator.format(*dynamic_value)

        try:
            return self.get_element((by_type, locator), timeout, multiple_elements)
        except ElementNotFoundException:
            return None

    def is_element_present(self,
                           element,
                           *values,
                           timeout: int = 1):

        try:
            if not values:
                return element.is_displayed()
            else:
                self.get_dynamic_element(element, *values, timeout=timeout, multiple_elements=False)
            return True
        except ElementNotFoundException:
            return False

    def get_driver(self):
        return self.driver

    def close_driver(self):
        return self.driver.quit()

    def is_driver_active(self):
        try:
            self.driver.execute_script("return window.document.title")
            return True
        except WebDriverException:
            return False
