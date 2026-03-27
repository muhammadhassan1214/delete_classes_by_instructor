from selenium.webdriver.common.by import By

BASE_URL = "https://atlas-api-gateway.heart.org/classManagement"

class Locators:
    # Login Page Locators
    SIGN_IN_BUTTON = (By.XPATH, "(//button[text()= 'Sign In | Sign Up'])[1]")
    USERNAME_INPUT = (By.ID, "Email")
    PASSWORD_INPUT = (By.ID, "Password")
    SUBMIT_BUTTON = (By.ID, "btnSignIn")
    PROFILE_ICON = (By.XPATH, "//span[@title= 'Nathaniel Shell' and contains(@class, 'Header_userName')]")

    # Dashboard Page Locators
    CLASSES_NAV = (By.ID, "Classes")
    TC_DROPDOWN = (By.CSS_SELECTOR, "button[title='Training Center/Site Classes']")
    SELECTED_ORGANIZATION = (By.XPATH, "//div[text()='Shell CPR, LLC.']")
    ORGANIZATION_INPUT = (By.CSS_SELECTOR, "input[aria-label=Organization]")
    ORGANIZATION_TO_SELECT = (By.CSS_SELECTOR, "div[title='Shell CPR, LLC.']")


class ApiEndpoints:
    CANCEL_CLASS = lambda x: f"{BASE_URL}/v1/classes/{x}"
    GET_CLASSES = lambda x: f"{BASE_URL}/v2/getClasses?size=100&page={x}&sort=startDateTime,desc"

    def get_headers(self: str) -> dict:
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'ext_id': 'dacbf678-f0cd-4f43-aaf0-7cd5058fb9f9',
            'origin': 'https://atlas.heart.org',
            'priority': 'u=1, i',
            'referer': 'https://atlas.heart.org/',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-jwt-token': self
        }
        return headers
