#!/usr/bin/env python3
"""
Test script to inspect the Aberdeen City Council bin collection form
"""

import requests
from bs4 import BeautifulSoup


def inspect_form():
    """Inspect the form structure on the Aberdeen City Council website."""
    url = "https://integration.aberdeencity.gov.uk/service/bin_collection_calendar___view"
    
    print(f"Fetching form from: {url}\n")
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms
        forms = soup.find_all('form')
        print(f"Found {len(forms)} form(s)\n")
        
        for i, form in enumerate(forms, 1):
            print(f"=== FORM {i} ===")
            print(f"Action: {form.get('action', 'N/A')}")
            print(f"Method: {form.get('method', 'N/A')}")
            print(f"ID: {form.get('id', 'N/A')}")
            print(f"Class: {form.get('class', 'N/A')}")
            print("\nForm Fields:")
            
            # Find all input fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                tag = inp.name
                field_type = inp.get('type', 'text')
                field_name = inp.get('name', 'N/A')
                field_id = inp.get('id', 'N/A')
                field_value = inp.get('value', '')
                field_placeholder = inp.get('placeholder', '')
                
                print(f"  - <{tag}> type='{field_type}' name='{field_name}' id='{field_id}'")
                if field_value:
                    print(f"    value: '{field_value}'")
                if field_placeholder:
                    print(f"    placeholder: '{field_placeholder}'")
                
                # For select fields, show options
                if tag == 'select':
                    options = inp.find_all('option')
                    if options:
                        print(f"    options: {[opt.get('value', opt.get_text(strip=True)) for opt in options[:5]]}")
            
            print("\n" + "-"*50 + "\n")
        
        # Also look for any javascript or data attributes that might indicate API endpoints
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tag(s)")
        
        # Look for form definition or API endpoints
        for script in scripts:
            script_text = script.get_text()
            if 'FormDefinition' in script_text or 'form_uri' in script_text:
                print(f"\n=== Form Definition Found ===")
                print(script_text[:1000])
                print("...")
                print()
        
        # Look for iframes
        iframes = soup.find_all('iframe')
        print(f"\nFound {len(iframes)} iframe(s)")
        for iframe in iframes:
            print(f"  - src: {iframe.get('src', 'N/A')}")
            print(f"    id: {iframe.get('id', 'N/A')}")
            print(f"    class: {iframe.get('class', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    inspect_form()
