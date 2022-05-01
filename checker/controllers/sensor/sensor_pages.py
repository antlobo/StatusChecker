import logging
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from checker.controllers.resources.custom_locator import Locator
from checker.controllers.resources.robot_driver import RobotDriver


class SensorPages:
    class Login:
        __logger = logging.getLogger(__name__)

        def button_confirm(self, driver):
            locators_list = [Locator(by=By.NAME, value="_PS02")]
            button_confirm = driver.get_element(locators_list)
            self.__logger.debug(f"Getting button to confirm: {button_confirm=}")
            return button_confirm

    class Information:
        __logger = logging.getLogger(__name__)

        def get_element(self, sensor_name: str,
                        driver: RobotDriver) -> tuple[Optional[WebElement], str]:

            locators_list = [Locator(by=By.XPATH,
                                     value=f"/html/body/table[4]/tbody/tr/td/table[1]/tbody/tr[{row}]/td[3]")
                             for row in range(0, 9)]

            row = -1
            column = 4 if "Temperatura" in sensor_name else 5
            for idx, locator in enumerate(locators_list):
                try:
                    element = driver.get_element([locator])
                    if element.text == sensor_name:
                        row = idx
                        break
                except Exception:
                    pass

            if row == -1:
                return None, f"[Error] There was not a coincidence for {sensor_name} in the sensor webpage"

            locators_list = [Locator(by=By.XPATH,
                                     value=f"/html/body/table[4]/tbody/tr/td/table[1]/tbody/tr[{row}]/td[{column}]")]
            try:
                element = driver.get_element(locators_list)
            except Exception:
                self.__logger.exception("There was a problem obtaining the information", exc_info=True)
                return None, "[Error] It was not found the value to retrieve"
            else:
                self.__logger.debug(f"For the: {sensor_name=}, got this {element.text=}")
                return element, "Success"
