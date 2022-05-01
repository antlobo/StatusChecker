# Standard library imports
import json
import logging.config
import os
from typing import NoReturn

# Third party imports
from dotenv import load_dotenv

# Local specific imports
from common.models import Service, ServiceLog, AppType
from database.data_manager import DataManager
from checker import BaseValidator as StatusChk


def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG') -> NoReturn:
    """
    Configure logging capabilities
    :param default_path: path to search for the logging configuration
    :param default_level: default level to log
    :param env_key: if using environment variable instead of default_path
    :return: it doesn't return a value
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def main():
    services, msg = dm.get_services()
    if not services:
        print(msg)
        exit(1)

    logs = []
    status_checker = StatusChk()
    for service in services:
        result, msg = status_checker.do_check_status(service)
        if isinstance(result, ServiceLog):
            logs.append(result)
    status_checker.close_driver()

    if logs:
        result, msg = dm.bulk_add_log_service(logs)
        if not result:
            print(msg)


if __name__ == "__main__":
    load_dotenv()
    setup_logging()
    dm = DataManager()
    main()
