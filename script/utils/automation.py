import os
import time
from dotenv import load_dotenv
from .static import Locators as Sl
from .helper import (
    click_element, input_element, _move_to_element,
    safe_navigate_to_url, check_element_exists,
    logger
)


load_dotenv()
url = "https://atlas.heart.org/"
base_dir = os.path.dirname(os.path.abspath(__file__))


def login(driver):
    def validate():
        if check_element_exists(driver, Sl.PROFILE_ICON, timeout=5):
            logger.info("Login successful.")
        else:
            logger.info("Login may have failed, dashboard not reached.")
    try:
        safe_navigate_to_url(driver, url)
        time.sleep(5)
        if check_element_exists(driver, Sl.PROFILE_ICON, timeout=5):
            logger.info("Already logged in.")
            validate()
            return
        signin_button = check_element_exists(driver, Sl.SIGN_IN_BUTTON, timeout=5)
        if signin_button:
            click_element(driver, Sl.SIGN_IN_BUTTON)
            input_element(driver, Sl.USERNAME_INPUT, os.getenv("AHA_USERNAME"))
            input_element(driver, Sl.PASSWORD_INPUT, os.getenv("AHA_PASSWORD"))
            click_element(driver, Sl.SUBMIT_BUTTON)
        validate()
    except Exception as e:
        logger.error(f"Login failed: {e}")


def capture_jwt_token(driver):
    try:
        token = driver.execute_script("return window.localStorage.getItem('userToken');")
        if token:
            return token
        else:
            logger.info("JWT token not found in local storage.")
            return None
    except Exception as e:
        logger.error(f"Failed to capture JWT token: {e}")
        return None


def navigate_to_class_listings(driver):
    try:
        _move_to_element(driver, Sl.CLASSES_NAV)
        time.sleep(0.5)
        click_element(driver, Sl.TC_DROPDOWN)
        time.sleep(2)
        ORG_ALREADY_SELECTED = check_element_exists(driver, Sl.SELECTED_ORGANIZATION, timeout=3)
        if ORG_ALREADY_SELECTED:
            logger.info("Organization already selected.\nSelected Organization `Shell CPR, LLC.`")
            return
        input_element(driver, Sl.ORGANIZATION_INPUT, "Shell CPR, LLC.")
        time.sleep(1)
        click_element(driver, Sl.ORGANIZATION_TO_SELECT)
        time.sleep(5)
    except Exception as e:
        logger.error(f"Navigation to class listings failed: {e}")
