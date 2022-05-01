# Standard library imports
import datetime as dt
import logging
from typing import Optional

# Third party imports
try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    raise ImportError("Packages bs4 and requests need to be installed")

# Local specific imports
from common.models import ServiceLog, Service


class StaticWeb:
    __logger = logging.getLogger(__name__)

    @classmethod
    def perform_static_validation(cls, service: Service) -> tuple[Optional[ServiceLog], str]:
        service_up = cls.__is_up(service.url)
        status_datetime = dt.datetime.now()
        route_list = service.route.split("|")
        routes_amount = len(route_list)

        if service_up:
            for route in route_list:
                try:
                    action, tag_name, tag_attr, attr_value = route.split(":")
                except ValueError:
                    cls.__logger.exception(f"[Error] The route {route} of the service {service.name} "
                                           f"doesn't follow the pattern {service.route_pattern}", exc_info=True)
                    return None, f"[Error] The route {route} of the service {service.name} " \
                                 f"doesn't follow the pattern {service.route_pattern}"
                else:
                    try:
                        response = requests.get(service.url)
                    except requests.exceptions.RequestException:
                        cls.__logger.exception(f"[Error] The route {route} of the service {service.name} "
                                               f"doesn't follow the pattern {service.route_pattern}", exc_info=True)
                        return None, f"[Error] The route {route} of the service {service.name} " \
                                     f"doesn't follow the pattern {service.route_pattern}"
                    else:
                        soup = BeautifulSoup(response.text, "html.parser")
                        value = soup.find(name=tag_name, attrs={tag_attr: attr_value})

                        if value and value.name == tag_name:
                            routes_amount -= 1

            if routes_amount < len(route_list):
                return ServiceLog(status="Running", status_date=status_datetime,
                                  other_data="", service=service), \
                       "Success"
            else:
                cls.__logger.error(f"[Error] It's possible that the service is Running but the tag name, "
                                   f"tag attribute and tag value may changed, update configuration for the "
                                   f"service: '{service.name}'")
                return None, f"[Error] It's possible that the service is Running but the tag name, tag attribute " \
                             f"and tag value may changed, update configuration for the service: '{service.name}'"

        elif service_up is not None:
            return ServiceLog(status="Not running", status_date=status_datetime,
                              other_data="", service=service), \
                   "Success"

        else:
            cls.__logger.error(f"[Error] Couldn't contact the service {service.name}")
            return None, f"[Error] Couldn't contact the service {service.name}"

    @classmethod
    def __is_up(cls, url):
        try:
            status = requests.get(url).status_code
        except Exception:
            return None
        else:
            return status < 400
