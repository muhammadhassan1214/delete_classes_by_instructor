# Delete Classes by Instructor

Run the browser automation to cancel classes for a selected instructor via a simple CustomTkinter desktop UI or the CLI.

## Setup
1. Install Python 3.10+ and Chrome.
2. (Optional) Create and activate a virtual environment.
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Add credentials to `.env` in the repo root:
```
AHA_USERNAME=your_username
AHA_PASSWORD=your_password
```

## Tkinter UI
Launch the desktop UI from the `script` folder:
```bash
cd script
python tk_ui.py
```
Pick an instructor from the dropdown, use the search to filter, toggle Light/Dark, then click **Start deleting**. The browser runs headless while cancelling classes.

## CLI (optional)
Run once for a specific instructor id (text before `/` in `script/utils/instructors.csv`):
```bash
cd script
python main.py 25083335760
```
Add `--headed` to watch the browser instead of headless mode.
