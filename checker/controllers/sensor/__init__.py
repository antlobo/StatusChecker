import logging
from datetime import datetime
from time import sleep
from typing import Optional, NoReturn

from common.models import Service, ServiceLog
from checker.controllers import BaseController
from .sensor_pages import SensorPages


class SensorController(BaseController):
    driver_initiated: bool = False
    logged_in: bool = False
    url: str = ""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self):
        super().__init__()
        self.logger.debug("Initiating webdriver")
        self.initiate_driver()

    def initiate_driver(self) -> NoReturn:
        if not self.driver_initiated:
            self.driver_initiated = True

    def login(self, url: str) -> NoReturn:
        if not self.logged_in:
            self.url = url
            self.robot_driver.driver.get(self.url)
            sleep(5)
            self.logger.info("Login in to the Sensor webpage")
            SensorPages.Login().button_confirm(self.robot_driver).click()
            self.logged_in = True

    def get_temperature(self, service: Service) -> tuple[Optional[ServiceLog], str]:
        self.logger.info(f"Getting temperature for the sensor {service.other_data1}")
        return self.get_status(service)

    def get_water_status(self, service: Service) -> tuple[Optional[ServiceLog], str]:
        self.logger.info(f"Getting water status for the sensor {service.other_data1}")
        return self.get_status(service)

    def get_status(self, service: Service) -> tuple[Optional[ServiceLog], str]:
        self.check_driver()
        sensor_name = service.other_data1
        status_datetime = datetime.now()

        result, msg = SensorPages.Information().get_element(sensor_name, self.robot_driver)

        if "[Error]" in msg:
            return result, msg

        try:
            status = result.text
        except AttributeError:
            return result, msg
        else:
            return ServiceLog(status="Running", status_date=status_datetime,
                              other_data=f"{sensor_name} - {status}", service=service), "Success"

    def refresh_page(self) -> NoReturn:
        self.robot_driver.driver.refresh()

    def quit_driver(self) -> NoReturn:
        self.logger.debug("Quitting webdriver")
        if self.robot_driver.is_driver_active():
            self.robot_driver.close_driver()

    def check_driver(self) -> NoReturn:
        if not self.robot_driver.is_driver_active():
            self.initiate_driver()
            sleep(5)
            self.login(self.url)
