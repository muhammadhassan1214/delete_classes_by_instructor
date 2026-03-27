import json
import requests
from ..static import ApiEndpoints


def extract_non_cancelled_class_ids(response: dict) -> tuple[bool, list[str]]:
    results = []

    data = response.get("data", {})
    items = data.get("items", [])

    pagination = data.get("pagination", {})
    is_last = pagination.get("isLast", False)

    for item in items:
        class_status = item.get("status")
        if class_status == "CANCELLED" or class_status == "COMPLETED":
            continue
        results.append(item.get("classId"))

    return is_last, results


def get_classes(page_number: int, jwt_token: str, instructor_id: str):
    url = ApiEndpoints.GET_CLASSES(page_number)
    headers = ApiEndpoints.get_headers(jwt_token)

    payload = json.dumps({
        "classFilters": {
            "isFirstTsSelected": False,
            "courseId": None,
            "disciplineCodes": None,
            "seatAvailability": None,
            "langCode": None,
            "location": None,
            "classStatus": None,
            "isPrivate": None,
            "applyFilter": False,
            "applyTsFilter": False,
            "page": page_number,
            "pageNumber": page_number,
            "parentId": 18260,
            "size": 100,
            "instructorIds": [f"{instructor_id}"],
            "selectedSort": "startDateTime",
            "sortOrder": "desc"
        }
    })

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return extract_non_cancelled_class_ids(response.json())
    else:
        print(f"Failed to get classes on page {page_number}: {response.status_code}")
        return None, []
