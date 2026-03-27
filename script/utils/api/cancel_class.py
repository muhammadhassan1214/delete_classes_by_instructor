import json
import logging
import requests
from ..static import ApiEndpoints

# Configure logger for this module
logger = logging.getLogger(__name__)


def cancel_class(class_id: str, jwt_token: str) -> bool:
    url = ApiEndpoints.CANCEL_CLASS(class_id)
    headers = ApiEndpoints.get_headers(jwt_token)

    payload = json.dumps({
        "class": {
            "isCancelled": True
        }
    })

    try:
        response = requests.patch(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            logger.info(f"Class {class_id} cancelled successfully.")
            return True

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while cancelling class {class_id}.")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while cancelling class {class_id}: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for class {class_id}: {e}")
        return False

    # Handle 400 and 422 responses
    if response.status_code in (400, 422):
        try:
            response_data = response.json()
            errors = response_data.get("error", {}).get("errors", [])

            if not errors:
                logger.warning(f"Received {response.status_code} for class {class_id} but no error details provided.")
                return False

            # Extract first error message for logging
            error_message = errors[0].get("message", "Unknown error")
            error_code = errors[0].get("errorCode", "Unknown")

            # Check for specific error codes
            if error_code == "class-management-service_2007":
                logger.info(f"Class {class_id}: {error_message} (already cancelled)")
                return True
            elif error_code == "class-management-service_2009":
                logger.warning(f"Class {class_id}: {error_message} (cannot be cancelled)")
                return False
            else:
                logger.error(f"Failed to cancel class {class_id}: {error_code} - {error_message}")
                return False

        except (ValueError, json.JSONDecodeError):
            logger.error(f"Failed to parse error response for class {class_id}: {response.status_code} - {response.text}")
            return False
        except KeyError as e:
            logger.error(f"Unexpected error response structure for class {class_id}: {e}")
            return False

    else:
        logger.error(f"Failed to cancel class {class_id}: HTTP {response.status_code} - {response.text}")
        return False
