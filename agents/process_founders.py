import csv
import json
import os
from wikipedia_lookup_agent import lookup

# File paths
INPUT_CSV = "/Users/aveekgoyal/ice_breaker/yc_founders.csv"
OUTPUT_JSON = "/Users/aveekgoyal/ice_breaker/agents/founders_wiki_data.json"
TRACKER_FILE = "/Users/aveekgoyal/ice_breaker/processed_rows.json"

def load_tracker():
    """Load the tracker file or create if doesn't exist"""
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {"last_processed_row": 0, "processed_founders": []}

def save_tracker(tracker_data):
    """Save the current state to tracker file"""
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker_data, f, indent=2)

def load_wiki_data():
    """Load existing wiki data or create empty dict"""
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, 'r') as f:
            return json.load(f)
    return {}

def save_wiki_data(wiki_data):
    """Save wiki data to JSON file"""
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(wiki_data, f, indent=2)

def process_founders():
    # Load tracker and wiki data
    tracker = load_tracker()
    wiki_data = load_wiki_data()
    last_processed_row = tracker["last_processed_row"]
    processed_founders = set(tracker["processed_founders"])

    # Read input CSV
    with open(INPUT_CSV, 'r') as input_file:
        reader = csv.DictReader(input_file)
        rows = list(reader)

    # Process rows starting from last processed row
    for idx, row in enumerate(rows[last_processed_row:], start=last_processed_row):
        founder_name = row["Founder Name"]
        
        # Skip if already processed
        if founder_name in processed_founders:
            print(f"Skipping {founder_name} - already processed")
            continue

        print(f"\nProcessing founder: {founder_name}")
        
        # Call Wikipedia lookup agent with enhanced description
        description = f"{row['Title']} at {row['Company Founded']}"
        if row['Description']:  # Add description if it exists
            description += f". {row['Description']}"
        if row['Company Founded']:  # Add company info if it exists
            description += f". Company: {row['Company Founded']}"
        
        result = lookup(
            name=founder_name,
            description=description
        )

        # Only store if there's a match
        if isinstance(result, dict) and not result.get("error"):
            if result.get("match") is False:
                print(f"✗ No Wikipedia match for {founder_name}: {result.get('reason', 'No reason provided')}")
            else:
                # Store the raw result only if it's a match
                wiki_data[founder_name] = result
                save_wiki_data(wiki_data)
                print(f"✓ Stored Wikipedia data for {founder_name}")
        else:
            print(f"✗ Error processing {founder_name}: {result.get('error', 'Unknown error')}")
        
        # Update tracker
        processed_founders.add(founder_name)
        tracker["processed_founders"] = list(processed_founders)
        tracker["last_processed_row"] = idx + 1
        save_tracker(tracker)

if __name__ == "__main__":
    process_founders()
