import time
import random
import argparse
from utils.api.get_classes import get_classes
from utils.api.cancel_class import cancel_class
from utils.helper import get_undetected_driver, logger
from utils.automation import (
    capture_jwt_token, login,
    navigate_to_class_listings
)
from typing import Optional

def _automation(instructor_id: str, *, headless: bool = True) -> None:
    """Run the cancellation automation for a specific instructor id."""
    if not instructor_id:
        raise ValueError("instructor_id is required")

    page_number = 0
    driver = get_undetected_driver(headless=headless)
    if driver is None:
        logger.info("Failed to initialize browser driver.")
        return

    jwt_token: Optional[str] = None
    try:
        login(driver)
        navigate_to_class_listings(driver)
        jwt_token = capture_jwt_token(driver)
        if jwt_token:
            logger.info("JWT token captured successfully.")
        else:
            logger.info("JWT token not captured; aborting.")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    if not jwt_token:
        return

    while True:
        islast_page, classes = get_classes(page_number, jwt_token, instructor_id)
        if islast_page is None:
            logger.info("Stopping: failed to fetch classes.")
            break

        if classes:
            logger.info(f"Found {len(classes)} classes on page {page_number + 1}.")
            for classId in classes:
                cancel_class(classId, jwt_token)
        else:
            logger.info(f"Classes on page {page_number + 1} are already cancelled.")

        logger.info(f"\n{'-'*50}\nFinished processing page {page_number + 1}.\n{'-'*50}")
        page_number += 1
        time.sleep(random.randint(1, 2))

        if islast_page:
            logger.info("--- All pages processed ---")
            logger.info(f"\n{'='*70}\nAll classes have been marked as canceled for the instructor: {instructor_id}.\n{'='*70}")
            break


def main(instructor_id: str, *, headless: bool = True) -> None:
    _automation(instructor_id, headless=headless)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cancel classes by instructor id")
    parser.add_argument("instructor_id", help="Instructor id (text before '/' in instructors.csv)")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode for debugging")
    args = parser.parse_args()

    main(args.instructor_id, headless=not args.headed)
