# Automated Inventory Dashboard

A Dash dashboard that visualizes inventory data. This repository includes a demo dataset (50% sampled rows) so the dashboard can run locally without access to the original cloud data.

---

# Important Note

- **Only `app.py` will run as-is** using the included demo CSVs.
- The other scripts — `watcher.py`, `clean.py`, and `runall.py` — are provided **for reference only**. They are configured for the original cloud pipeline and will **not** run locally without access to that environment.

---

## Quick Start (Windows PowerShell)

1. Open PowerShell in the project folder.
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1


3.Install dependencies:

powershell
Copy
Edit
pip install -r requirements.txt

4.python app.py


---

## Requirements
- Python 3.9+ recommended
- Dash
- Pandas
- Plotly
- xlsxwriter
- waitress
- dash_auth


