# Standard library imports
from time import sleep
from typing import Optional
import logging

# Third party imports
try:
    from selenium.webdriver import Firefox
    from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options
except ImportError:
    logging.warning("Package selenium need to be installed")
    raise ImportError("Package selenium need to be installed")

from common.models import AppType, Service, ServiceLog
from .controllers.sensor import SensorController
from .controllers.web import StaticWeb


class BaseValidator:

    def __init__(self):
        self.__st_web = StaticWeb()
        self.__sensor = SensorController()
        self.__logger = logging.getLogger(__name__)

    def do_check_status(self, service: Service) -> tuple[Optional[ServiceLog], str]:
        self.__logger.info(f"Initiating validation of {service.name}")

        if service.app_type == AppType.T_SENSOR.value:
            self.__sensor.login(service.url)
            sleep(3)
            result, msg = self.__sensor.get_temperature(service)

        elif service.app_type == AppType.W_SENSOR.value:
            self.__sensor.login(service.url)
            sleep(3)
            result, msg = self.__sensor.get_water_status(service)

        # elif service.app_type == AppType.ZABBIX.value:
        #     result, msg = None, f"AppType = : {service.app_type}"

        elif service.app_type == AppType.WEBAPP.value:
            result, msg = self.__st_web.perform_static_validation(service)

        else:
            self.__logger.warning(f"Attempted to validate {service.name}, "
                                  f"but the {service.app_type} has not been configured to be validated")
            result, msg = None, f"[X] There is not configured this type of check: {service.app_type}"

        self.__logger.info(f"Ending validation of {service.name} with a message of: '{msg}'")
        return result, msg

    def close_driver(self):
        self.__sensor.quit_driver()
