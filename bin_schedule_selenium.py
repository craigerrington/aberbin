#!/usr/bin/env python3
"""
Aberdeen City Council Bin Collection Schedule Checker (Selenium Version)

This script retrieves bin collection schedules from the Aberdeen City Council website
based on postcode and street number input using Selenium to handle JavaScript forms.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import time


class BinScheduleChecker:
    def __init__(self, headless=True):
        """
        Initialize the bin schedule checker with Selenium.
        
        Args:
            headless (bool): Run browser in headless mode (no GUI)
        """
        self.url = "https://integration.aberdeencity.gov.uk/service/bin_collection_calendar___view"
        self.headless = headless
        self.driver = None
    
    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # Use webdriver-manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
    
    def get_bin_schedule(self, postcode, street_number):
        """
        Retrieve bin collection schedule for a given postcode and street number.
        
        Args:
            postcode (str): The postcode (e.g., 'AB10 1AB')
            street_number (str): The street number
            
        Returns:
            dict: Bin collection schedule information
        """
        try:
            print(f"Loading webpage...")
            self.driver.get(self.url)
            
            # Wait for the iframe to load
            print("Waiting for form to load...")
            wait = WebDriverWait(self.driver, 20)
            
            # Switch to the iframe containing the form
            iframe = wait.until(EC.presence_of_element_located((By.ID, "fillform-frame-1")))
            self.driver.switch_to.frame(iframe)
            
            print("Form loaded. Looking for input fields...")
            
            # Wait a bit more for the form fields to be ready
            time.sleep(2)
            
            # Try to find postcode and street number fields
            # Common patterns for field identification
            field_patterns = [
                # By ID
                ("id", ["postcode", "Postcode", "post_code", "txtPostcode"]),
                ("id", ["street", "Street", "street_number", "number", "housenumber", "txtStreet"]),
                # By name
                ("name", ["postcode", "Postcode", "post_code"]),
                ("name", ["street", "Street", "street_number", "number", "housenumber"]),
                # By placeholder
                ("placeholder", ["postcode", "Postcode", "post code"]),
                ("placeholder", ["street", "Street", "number"]),
            ]
            
            postcode_field = None
            number_field = None
            
            # Try to find input fields
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            all_selects = self.driver.find_elements(By.TAG_NAME, "select")
            
            print(f"Found {len(all_inputs)} input fields and {len(all_selects)} select fields")
            
            # Print all visible fields for debugging
            for i, inp in enumerate(all_inputs[:20]):  # Limit to first 20 for debugging
                try:
                    field_type = inp.get_attribute("type")
                    field_name = inp.get_attribute("name")
                    field_id = inp.get_attribute("id")
                    field_placeholder = inp.get_attribute("placeholder")
                    is_visible = inp.is_displayed()
                    
                    if is_visible and field_type not in ["hidden", "submit", "button"]:
                        print(f"  Input {i+1}: type={field_type}, name={field_name}, id={field_id}, placeholder={field_placeholder}")
                        
                        # Try to identify postcode field
                        if not postcode_field:
                            if any(term in str(field_name).lower() for term in ["post", "code"]) or \
                               any(term in str(field_id).lower() for term in ["post", "code"]) or \
                               any(term in str(field_placeholder).lower() for term in ["post", "code"]):
                                postcode_field = inp
                                print(f"    -> Identified as POSTCODE field")
                        
                        # Try to identify street number field
                        if not number_field:
                            if any(term in str(field_name).lower() for term in ["street", "number", "house", "property"]) or \
                               any(term in str(field_id).lower() for term in ["street", "number", "house", "property"]) or \
                               any(term in str(field_placeholder).lower() for term in ["street", "number", "house", "property"]):
                                number_field = inp
                                print(f"    -> Identified as NUMBER field")
                except:
                    pass
            
            # Check select fields for address selection
            for i, sel in enumerate(all_selects):
                try:
                    field_name = sel.get_attribute("name")
                    field_id = sel.get_attribute("id")
                    is_visible = sel.is_displayed()
                    
                    if is_visible:
                        print(f"  Select {i+1}: name={field_name}, id={field_id}")
                except:
                    pass
            
            # Handle two-step process: postcode search first
            if postcode_field and not number_field:
                print(f"\nThis appears to be a two-step form (postcode search first)")
                print(f"Step 1: Entering postcode: {postcode}")
                postcode_field.clear()
                postcode_field.send_keys(postcode)
                
                # Find and click search button
                search_button = None
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']"))
                    buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']"))
                except Exception as e:
                    print(f"Error finding buttons: {e}")
                    buttons = []
                
                for btn in buttons:
                    try:
                        if btn.is_displayed():
                            btn_text = (btn.text or "").lower()
                            btn_value = (btn.get_attribute("value") or "").lower()
                            btn_id = (btn.get_attribute("id") or "").lower()
                            
                            if any(term in btn_text + btn_value + btn_id for term in ["search", "find", "look"]):
                                search_button = btn
                                print(f"Found search button: {btn.text or btn.get_attribute('value') or btn.get_attribute('id')}")
                                break
                    except:
                        pass
                
                if not search_button:
                    # Try to submit the form by pressing Enter
                    print("No search button found, trying to submit via Enter key...")
                    from selenium.webdriver.common.keys import Keys
                    postcode_field.send_keys(Keys.RETURN)
                    time.sleep(3)
                else:
                    print("Clicking search button...")
                    try:
                        search_button.click()
                    except:
                        # If click fails, try JavaScript click
                        self.driver.execute_script("arguments[0].click();", search_button)
                    time.sleep(3)
                
                # Now look for address selection dropdown or list
                print("\nStep 2: Looking for address selection...")
                
                # Wait for the select dropdown to appear
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
                except TimeoutException:
                    print("Timeout waiting for address dropdown")
                
                all_selects = self.driver.find_elements(By.TAG_NAME, "select")
                
                address_select = None
                for sel in all_selects:
                    if sel.is_displayed():
                        field_name = sel.get_attribute("name") or ""
                        field_id = sel.get_attribute("id") or ""
                        if any(term in field_name.lower() + field_id.lower() for term in ["address", "property", "street", "uprn"]):
                            address_select = sel
                            print(f"Found address select: name={field_name}, id={field_id}")
                            break
                
                if not address_select:
                    return {"error": "Could not find address selection dropdown after postcode search"}
                
                # Get all options and try to find matching street number
                from selenium.webdriver.support.ui import Select
                select_element = Select(address_select)
                options = select_element.options
                
                print(f"Found {len(options)} address options")
                
                # Try to match street number
                matched_option = None
                for option in options:
                    option_text = option.text
                    print(f"  Option: {option_text[:100]}")
                    
                    # Check if street number appears at start of address
                    if option_text.strip().startswith(street_number + " ") or \
                       option_text.strip().startswith(street_number + ","):
                        matched_option = option
                        print(f"  ✓ Matched!")
                        break
                
                if not matched_option and len(options) > 1:
                    # Show available options and ask which one
                    print("\n⚠️  Could not automatically match street number.")
                    print(f"Available addresses for postcode {postcode}:")
                    for i, option in enumerate(options[1:], 1):  # Skip first option (usually blank)
                        print(f"  {i}. {option.text}")
                    return {
                        "error": f"Could not find address '{street_number}' in postcode '{postcode}'",
                        "addresses": [opt.text for opt in options[1:]]
                    }
                
                if matched_option:
                    print(f"\nSelecting address: {matched_option.text}")
                    matched_option.click()
                    time.sleep(2)
                else:
                    return {"error": "No addresses found for this postcode"}
                
                # Look for continue/submit button
                continue_button = None
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']"))
                
                for btn in buttons:
                    try:
                        if btn.is_displayed():
                            btn_text = (btn.text or "").lower()
                            btn_value = (btn.get_attribute("value") or "").lower()
                            
                            if any(term in btn_text + btn_value for term in ["continue", "submit", "next", "view"]):
                                continue_button = btn
                                print(f"Found continue button: {btn.text or btn.get_attribute('value')}")
                                break
                    except:
                        pass
                
                if continue_button:
                    print("Submitting address selection...")
                    continue_button.click()
                    time.sleep(3)
                
            elif postcode_field and number_field:
                # Single-step form
                print(f"\nFilling in postcode: {postcode}")
                postcode_field.clear()
                postcode_field.send_keys(postcode)
                
                print(f"Filling in street number: {street_number}")
                number_field.clear()
                number_field.send_keys(street_number)
                
                # Look for submit button
                submit_button = None
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']"))
                
                for btn in buttons:
                    btn_text = btn.text.lower()
                    btn_value = btn.get_attribute("value")
                    if btn_value:
                        btn_text += " " + btn_value.lower()
                    
                    if any(term in btn_text for term in ["search", "submit", "find", "next", "continue"]):
                        if btn.is_displayed():
                            submit_button = btn
                            print(f"Found submit button: {btn.text or btn.get_attribute('value')}")
                            break
                
                if not submit_button:
                    return {"error": "Could not find submit button"}
                
                print("Submitting form...")
                submit_button.click()
                time.sleep(3)
            else:
                return {
                    "error": "Could not identify form fields. The website structure may have changed.",
                    "debug": f"Found {len(all_inputs)} inputs and {len(all_selects)} selects"
                }
            
            # Try to extract results
            print("Extracting results...")
            
            # Wait a bit more for JavaScript to populate the date fields
            time.sleep(3)
            
            # Extract bin collection dates directly from the form fields
            schedule = {"collections": []}
            
            # Define bin types and their corresponding field patterns
            bin_types = {
                "Mixed Recycling": "RecyclingDate",
                "Food & Garden Waste": "GardenDate",
                "General Waste": "GeneralDate"
            }
            
            for bin_name, field_prefix in bin_types.items():
                dates = []
                # Try to get up to 8 dates for each bin type
                for i in range(1, 9):
                    field_id = f"{field_prefix}{i}"
                    try:
                        element = self.driver.find_element(By.ID, field_id)
                        date_value = element.get_attribute("value")
                        if date_value and date_value.strip():
                            dates.append(date_value.strip())
                    except NoSuchElementException:
                        continue
                    except:
                        break
                
                if dates:
                    schedule["collections"].append({
                        "bin_type": bin_name,
                        "dates": dates
                    })
            
            # Also try traditional parsing as fallback
            if not schedule.get("collections"):
                page_source = self.driver.page_source
                schedule = self.parse_results(page_source)
                
                # Get body text for debugging
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    schedule["page_text"] = body_text[:2000]
                except:
                    pass
            
            return schedule
            
        except TimeoutException:
            return {"error": "Timeout waiting for page to load"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "type": type(e).__name__}
    
    def parse_results(self, html):
        """
        Parse bin collection schedule from the results page.
        
        Args:
            html (str): HTML content of the results page
            
        Returns:
            dict: Parsed schedule information
        """
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html, 'html.parser')
        
        schedule = {
            "collections": [],
            "raw_text": []
        }
        
        # Look for date patterns in the HTML
        # Common date formats: DD/MM/YYYY, DD-MM-YYYY, Monday DD Month YYYY, etc.
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
        
        # Look for elements that pair bin types with dates
        bin_keywords = ['recycling', 'waste', 'garden', 'food', 'general', 'mixed', 'glass']
        
        # Check all text nodes for bin type + date combinations
        for element in soup.find_all(['div', 'span', 'p', 'td', 'li', 'label']):
            text = element.get_text(strip=True)
            
            # Check if this element contains a bin keyword
            for keyword in bin_keywords:
                if keyword in text.lower() and len(text) < 100:
                    # Look for dates in this element or nearby elements
                    dates = re.findall(date_pattern, text, re.IGNORECASE)
                    if dates:
                        schedule["collections"].append({
                            "bin_type": text,
                            "date": ', '.join(dates)
                        })
                        break
        
        # Look for input fields with date values (common in forms)
        for input_field in soup.find_all('input'):
            field_id = input_field.get('id', '')
            field_name = input_field.get('name', '')
            field_value = input_field.get('value', '')
            
            # Check if this looks like a date field for a bin
            if any(keyword in field_id.lower() + field_name.lower() for keyword in bin_keywords):
                if field_value and re.search(date_pattern, field_value, re.IGNORECASE):
                    # Find the label for this field
                    label = soup.find('label', {'for': field_id})
                    if label:
                        bin_type = label.get_text(strip=True)
                    else:
                        bin_type = field_id.replace('_', ' ').title()
                    
                    schedule["collections"].append({
                        "bin_type": bin_type,
                        "date": field_value
                    })
        
        # Look for tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    text1 = cells[0].get_text(strip=True)
                    text2 = cells[1].get_text(strip=True)
                    if text1 and text2 and any(keyword in text1.lower() for keyword in bin_keywords):
                        schedule["collections"].append({
                            "bin_type": text1,
                            "date": text2
                        })
        
        # Look for lists
        lists = soup.find_all(['ul', 'ol', 'dl'])
        for lst in lists:
            items = lst.find_all(['li', 'dt', 'dd'])
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) > 5:
                    schedule["raw_text"].append(text)
        
        # Look for divs with specific classes that might contain schedule info
        for div in soup.find_all('div'):
            text = div.get_text(strip=True)
            if any(keyword in text.lower() for keyword in ['bin', 'collection', 'waste', 'recycling']):
                if len(text) > 10 and len(text) < 200:
                    schedule["raw_text"].append(text)
        
        # Deduplicate collections
        seen = set()
        unique_collections = []
        for col in schedule["collections"]:
            key = (col["bin_type"].lower(), col["date"].lower())
            if key not in seen:
                seen.add(key)
                unique_collections.append(col)
        schedule["collections"] = unique_collections
        
        return schedule
    
    def display_schedule(self, schedule):
        """
        Display the bin collection schedule in a user-friendly format.
        
        Args:
            schedule (dict): The bin collection schedule
        """
        from datetime import datetime
        
        if "error" in schedule:
            print(f"\n❌ Error: {schedule['error']}")
            if "debug" in schedule:
                print(f"Debug info: {schedule['debug']}")
            return
        
        print("\n" + "="*50)
        print("BIN COLLECTION SCHEDULE")
        print("="*50)
        
        if schedule.get("collections"):
            # Find the next collection across all bin types
            next_collection = None
            next_date = None
            
            for collection in schedule["collections"]:
                if "dates" in collection and collection["dates"]:
                    first_date_str = collection["dates"][0]
                    try:
                        # Parse the date
                        parsed_date = datetime.strptime(first_date_str, "%A %d %B %Y")
                        if next_date is None or parsed_date < next_date:
                            next_date = parsed_date
                            next_collection = {
                                "bin_type": collection["bin_type"],
                                "date": first_date_str
                            }
                    except:
                        pass
            
            # Display next collection prominently
            if next_collection:
                print(f"\n🔔 YOUR NEXT COLLECTION:")
                print("="*50)
                print(f"   {next_collection['bin_type']}")
                print(f"   {next_collection['date']}")
                print("="*50)
            
            print("\n📅 All Upcoming Collections:")
            print("-"*50)
            for collection in schedule["collections"]:
                if "dates" in collection:
                    # Multiple dates format
                    print(f"\n🗑️  {collection['bin_type']}:")
                    for date in collection["dates"]:
                        print(f"    • {date}")
                elif "date" in collection:
                    # Single date format
                    print(f"  • {collection['bin_type']}: {collection['date']}")
        
        if schedule.get("raw_text"):
            print("\n📄 Additional Information:")
            print("-"*50)
            for text in schedule["raw_text"][:10]:  # Limit to first 10 items
                print(f"  • {text}")
        
        if schedule.get("page_text"):
            print("\n📄 Page Content:")
            print("-"*50)
            print(schedule["page_text"][:500])
            print("...")
        
        if schedule.get("addresses"):
            print("\n📍 Available Addresses:")
            print("-"*50)
            for i, addr in enumerate(schedule["addresses"][:10], 1):
                print(f"  {i}. {addr}")
        
        if not schedule.get("collections") and not schedule.get("raw_text") and not schedule.get("page_text"):
            print("\n⚠️  No collection information found.")
            print("Please verify your postcode and street number are correct.")
        
        print("="*50 + "\n")


def main():
    """Main function to run the bin schedule checker."""
    print("Aberdeen City Council - Bin Collection Schedule Checker")
    print("-" * 55)
    
    # Get user input
    if len(sys.argv) == 3:
        street_number = sys.argv[1]
        postcode = sys.argv[2]
    else:
        print("\nPlease enter your details:")
        street_number = input("Street Number: ").strip()
        postcode = input("Postcode (e.g., AB10 1AB): ").strip().upper()
    
    if not street_number or not postcode:
        print("\n❌ Error: Both street number and postcode are required.")
        sys.exit(1)
    
    # Create checker and run
    checker = BinScheduleChecker(headless=True)
    
    try:
        checker.setup_driver()
        schedule = checker.get_bin_schedule(postcode, street_number)
        checker.display_schedule(schedule)
    finally:
        checker.close_driver()


if __name__ == "__main__":
    main()
