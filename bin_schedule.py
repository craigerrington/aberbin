#!/usr/bin/env python3
"""
Aberdeen City Council Bin Collection Schedule Checker

This script retrieves bin collection schedules from the Aberdeen City Council website
based on postcode and street number input.
"""

import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime


class BinScheduleChecker:
    def __init__(self):
        self.base_url = "https://integration.aberdeencity.gov.uk"
        self.service_url = f"{self.base_url}/service/bin_collection_calendar___view"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
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
            # First, get the form page to extract any necessary tokens/session data
            print(f"Fetching bin schedule for {street_number}, postcode {postcode}...")
            
            response = self.session.get(self.service_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the form and its action URL
            form = soup.find('form')
            if not form:
                return {"error": "Could not find form on the page"}
            
            # Extract form action and method
            form_action = form.get('action', '')
            form_method = form.get('method', 'post').lower()
            
            # Build the full action URL
            if form_action.startswith('http'):
                action_url = form_action
            elif form_action.startswith('/'):
                action_url = f"{self.base_url}{form_action}"
            else:
                action_url = f"{self.service_url}/{form_action}" if form_action else self.service_url
            
            # Extract all form fields including hidden ones
            form_data = {}
            for input_field in form.find_all(['input', 'select']):
                field_name = input_field.get('name')
                field_value = input_field.get('value', '')
                field_type = input_field.get('type', 'text')
                
                if field_name:
                    # Skip submit buttons unless needed
                    if field_type not in ['submit', 'button']:
                        form_data[field_name] = field_value
            
            # Update with user-provided data
            # Common field names for postcode and street number
            postcode_fields = ['postcode', 'Postcode', 'post_code', 'POSTCODE']
            number_fields = ['street_number', 'number', 'house_number', 'Street', 'streetNumber']
            
            # Try to identify correct field names
            for field in postcode_fields:
                if field in form_data or any(field.lower() in k.lower() for k in form_data.keys()):
                    matching_key = next((k for k in form_data.keys() if field.lower() in k.lower()), field)
                    form_data[matching_key] = postcode
                    break
            else:
                # If no matching field found, add common ones
                form_data['postcode'] = postcode
            
            for field in number_fields:
                if field in form_data or any(field.lower() in k.lower() for k in form_data.keys()):
                    matching_key = next((k for k in form_data.keys() if field.lower() in k.lower()), field)
                    form_data[matching_key] = street_number
                    break
            else:
                form_data['number'] = street_number
            
            # Submit the form
            if form_method == 'get':
                submit_response = self.session.get(action_url, params=form_data)
            else:
                submit_response = self.session.post(action_url, data=form_data)
            
            submit_response.raise_for_status()
            
            # Parse the results
            result_soup = BeautifulSoup(submit_response.text, 'html.parser')
            
            # Extract bin collection information
            schedule = self.parse_bin_schedule(result_soup)
            
            return schedule
            
        except requests.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def parse_bin_schedule(self, soup):
        """
        Parse the bin collection schedule from the response HTML.
        
        Args:
            soup (BeautifulSoup): Parsed HTML response
            
        Returns:
            dict: Parsed bin collection schedule
        """
        schedule = {
            "address": None,
            "collections": []
        }
        
        # Look for address information
        address_elem = soup.find(['h2', 'h3', 'div'], class_=lambda x: x and 'address' in x.lower() if x else False)
        if address_elem:
            schedule["address"] = address_elem.get_text(strip=True)
        
        # Look for bin collection dates - these might be in tables, lists, or divs
        # Try table format
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    bin_type = cells[0].get_text(strip=True)
                    date = cells[1].get_text(strip=True)
                    if bin_type and date:
                        schedule["collections"].append({
                            "bin_type": bin_type,
                            "date": date
                        })
        
        # Try list format
        if not schedule["collections"]:
            lists = soup.find_all(['ul', 'ol'])
            for lst in lists:
                items = lst.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if text:
                        schedule["collections"].append({
                            "text": text
                        })
        
        # If still no collections found, look for any divs with dates
        if not schedule["collections"]:
            # Look for elements containing date patterns
            all_text = soup.get_text()
            schedule["raw_text"] = all_text[:1000]  # First 1000 chars for debugging
        
        return schedule
    
    def display_schedule(self, schedule):
        """
        Display the bin collection schedule in a user-friendly format.
        
        Args:
            schedule (dict): The bin collection schedule
        """
        if "error" in schedule:
            print(f"\n❌ Error: {schedule['error']}")
            return
        
        print("\n" + "="*50)
        print("BIN COLLECTION SCHEDULE")
        print("="*50)
        
        if schedule.get("address"):
            print(f"\n📍 Address: {schedule['address']}")
        
        if schedule.get("collections"):
            print("\n📅 Upcoming Collections:")
            print("-"*50)
            
            for collection in schedule["collections"]:
                if "bin_type" in collection:
                    print(f"  • {collection['bin_type']}: {collection['date']}")
                elif "text" in collection:
                    print(f"  • {collection['text']}")
        elif schedule.get("raw_text"):
            print("\n📄 Raw response (for debugging):")
            print(schedule["raw_text"])
        else:
            print("\n⚠️  No collection information found.")
            print("This might mean:")
            print("  - Invalid postcode or street number")
            print("  - The website format has changed")
            print("  - The address is not in the system")
        
        print("="*50 + "\n")


def main():
    """Main function to run the bin schedule checker."""
    checker = BinScheduleChecker()
    
    print("Aberdeen City Council - Bin Collection Schedule Checker")
    print("-" * 55)
    
    # Get user input
    if len(sys.argv) == 3:
        # Command line arguments provided
        street_number = sys.argv[1]
        postcode = sys.argv[2]
    else:
        # Interactive mode
        print("\nPlease enter your details:")
        street_number = input("Street Number: ").strip()
        postcode = input("Postcode (e.g., AB10 1AB): ").strip().upper()
    
    if not street_number or not postcode:
        print("\n❌ Error: Both street number and postcode are required.")
        sys.exit(1)
    
    # Get and display the schedule
    schedule = checker.get_bin_schedule(postcode, street_number)
    checker.display_schedule(schedule)


if __name__ == "__main__":
    main()
