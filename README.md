# Aberdeen City Council Bin Collection Schedule Checker

A Python program that retrieves bin collection schedules from the Aberdeen City Council website based on postcode and street number input.

## Features

- 🔍 Looks up bin collection schedules using postcode and street number
- 📅 Displays upcoming collection dates for different bin types
- 💻 Works in both interactive and command-line modes
- 🌐 Retrieves data directly from the Aberdeen City Council website
- 🤖 Uses Selenium to handle JavaScript-rendered forms automatically

## Installation

1. Make sure you have Python 3.6+ installed

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or on Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode

Run the Selenium-based script without arguments to enter interactive mode:

```bash
python bin_schedule_selenium.py
```

You'll be prompted to enter:
- Street Number
- Postcode (e.g., AB10 1AB)

### Command Line Mode

Provide the street number and postcode as arguments:

```bash
python bin_schedule_selenium.py "123" "AB10 1AB"
```

## Example

The program automatically:
1. Searches for addresses matching your postcode
2. Selects the address with your street number
3. Shows you which bin collection is happening next
4. Displays the next 8 collection dates for each bin type

```bash
$ python bin_schedule_selenium.py "123" "AB10 1AB"

Aberdeen City Council - Bin Collection Schedule Checker
-------------------------------------------------------
Step 1: Entering postcode: AB10 1AB
Step 2: Looking for address selection...
Found 15 address options
✓ Matched: 123 Example Street, Aberdeen, AB10 1AB

==================================================
BIN COLLECTION SCHEDULE
==================================================

🔔 YOUR NEXT COLLECTION:
==================================================
   Mixed Recycling
   Wednesday 10 December 2025
==================================================

📅 All Upcoming Collections:
--------------------------------------------------

🗑️  Mixed Recycling:
    • Wednesday 10 December 2025
    • Wednesday 24 December 2025
    • Wednesday 07 January 2026
    (... 5 more dates)

🗑️  Food & Garden Waste:
    • Wednesday 10 December 2025
    • Wednesday 24 December 2025
    (... 6 more dates)

🗑️  General Waste:
    • Wednesday 17 December 2025
    • Wednesday 31 December 2025
    (... 6 more dates)
==================================================
```
## Files

- `bin_schedule_selenium.py` - Main script using Selenium to handle JavaScript forms
- `inspect_form.py` - Utility script to inspect the website's form structure
- `requirements.txt` - Python package dependencies

## Notes

- This program interacts with the Aberdeen City Council website, so it may break if the website structure changes
- Make sure you have an internet connection when running the script
- The postcode should be in UK format (e.g., AB10 1AB)
- The Selenium version automatically handles the JavaScript-rendered form in the iframe
- Chrome WebDriver is automatically downloaded and managed by webdriver-manager
- Google Chrome (for Selenium version)
- requests
- beautifulsoup4
- lxml
- selenium
- webdriver-managerests
- beautifulsoup4
- lxml

## Troubleshooting

If you encounter issues:

1. **No collection information found**: Verify that your postcode and street number are correct
2. **Network errors**: Check your internet connection
3. **Website structure changed**: The Aberdeen City Council website may have updated its format

## License

This project is provided as-is for personal use.
