import os
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(BASE_DIR, "instructors.csv")


def load_instructors(csv_path: str = DEFAULT_CSV_PATH) -> List[Dict[str, str]]:
    """Load instructors from CSV column 1 and split into id/name parts."""
    instructors: List[Dict[str, str]] = []

    if not os.path.exists(csv_path):
        return instructors

    with open(csv_path, "r", encoding="utf-8") as csvfile:
        for raw_line in csvfile.readlines():
            entry = raw_line.strip()
            if not entry:
                continue

            if "/" in entry:
                instructor_id, name = entry.split("/", 1)
                instructor_id = instructor_id.strip()
                name = name.strip()
            else:
                instructor_id = entry.strip()
                name = ""

            instructors.append({
                "id": instructor_id,
                "name": name,
                "label": entry
            })

    return instructors

