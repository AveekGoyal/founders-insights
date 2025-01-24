import json
import csv
import os
from typing import Dict, Any, List

class WikiDataConverter:
    def __init__(self, input_json_path: str, output_csv_path: str, tracking_file: str):
        self.input_json_path = input_json_path
        self.output_csv_path = output_csv_path
        self.tracking_file = tracking_file
        self.tracking_data = self.load_tracking()
        self.max_experiences = self._get_max_experiences()
        
    def _get_max_experiences(self) -> int:
        """Get the maximum number of experiences across all founders"""
        max_exp = 0
        with open(self.input_json_path, 'r') as f:
            data = json.load(f)
            for founder_data in data.values():
                exp_count = len(founder_data.get('career', {}).get('experience', []))
                max_exp = max(max_exp, exp_count)
        return max_exp
        
    def load_tracking(self) -> Dict[str, Any]:
        """Load or create tracking data"""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return {
            "last_processed_founder": None,
            "total_founders_processed": 0,
            "conversion_status": "incomplete"
        }
    
    def save_tracking(self):
        """Save tracking data"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)
    
    def format_list(self, items: list) -> str:
        """Convert list to pipe-separated string"""
        return "|".join(items) if items else ""
    
    def flatten_experience(self, experience: List[Dict]) -> Dict[str, str]:
        """Flatten experience data into a dictionary with company-prefixed keys"""
        flattened = {}
        
        for idx, exp in enumerate(experience, 1):
            prefix = f"experience_{idx}"
            company = exp.get('company', '')
            roles = exp.get('roles', [])
            
            if roles:
                # Take the most recent/first role
                role = roles[0]
                flattened.update({
                    f"{prefix}_company": company,
                    f"{prefix}_title": role.get('title', ''),
                    f"{prefix}_duration": role.get('duration', ''),
                    f"{prefix}_description": role.get('description', ''),
                    f"{prefix}_responsibilities": self.format_list(role.get('responsibilities', [])),
                    f"{prefix}_achievements": self.format_list(role.get('achievements', []))
                })
        
        # Ensure all experiences up to max_experiences are represented
        for idx in range(1, self.max_experiences + 1):
            prefix = f"experience_{idx}"
            if f"{prefix}_company" not in flattened:
                flattened.update({
                    f"{prefix}_company": "",
                    f"{prefix}_title": "",
                    f"{prefix}_duration": "",
                    f"{prefix}_description": "",
                    f"{prefix}_responsibilities": "",
                    f"{prefix}_achievements": ""
                })
        
        return flattened
    
    def convert(self):
        """Convert JSON data to CSV"""
        # Read input JSON
        with open(self.input_json_path, 'r') as f:
            data = json.load(f)
            
        # Define base CSV headers
        base_headers = [
            'founder_name',
            'short_description',
            'education_degree',
            'education_institution',
            'education_field',
            'current_role_title',
            'current_role_company',
            'current_role_description',
            'current_role_duration',
            'current_role_achievements',
            'total_years_experience'
        ]
        
        # Add experience headers for all experiences
        experience_headers = []
        for i in range(1, self.max_experiences + 1):
            prefix = f"experience_{i}"
            experience_headers.extend([
                f"{prefix}_company",
                f"{prefix}_title",
                f"{prefix}_duration",
                f"{prefix}_description",
                f"{prefix}_responsibilities",
                f"{prefix}_achievements"
            ])
        
        headers = base_headers + experience_headers + ['source_url']
        
        # Create or append to CSV
        mode = 'a' if self.tracking_data["last_processed_founder"] else 'w'
        write_headers = mode == 'w'
        
        with open(self.output_csv_path, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if write_headers:
                writer.writeheader()
            
            # Process each founder
            start_processing = not self.tracking_data["last_processed_founder"]
            for founder_name, founder_data in data.items():
                # Skip until last processed founder
                if not start_processing:
                    if founder_name == self.tracking_data["last_processed_founder"]:
                        start_processing = True
                    continue
                
                # Extract base data
                row = {
                    'founder_name': founder_name,
                    'short_description': founder_data.get('short_description', ''),
                    'education_degree': founder_data.get('education', {}).get('degree', ''),
                    'education_institution': founder_data.get('education', {}).get('institution', ''),
                    'education_field': founder_data.get('education', {}).get('field', ''),
                    'current_role_title': founder_data.get('career', {}).get('current_role', {}).get('title', ''),
                    'current_role_company': founder_data.get('career', {}).get('current_role', {}).get('company', ''),
                    'current_role_description': founder_data.get('career', {}).get('current_role', {}).get('description', ''),
                    'current_role_duration': founder_data.get('career', {}).get('current_role', {}).get('duration', ''),
                    'current_role_achievements': self.format_list(
                        founder_data.get('career', {}).get('current_role', {}).get('achievements', [])
                    ),
                    'total_years_experience': founder_data.get('career', {}).get('total_years_experience', ''),
                    'source_url': founder_data.get('source_url', '')
                }
                
                # Add flattened experience data
                experience_data = self.flatten_experience(
                    founder_data.get('career', {}).get('experience', [])
                )
                row.update(experience_data)
                
                writer.writerow(row)
                
                # Update tracking
                self.tracking_data["last_processed_founder"] = founder_name
                self.tracking_data["total_founders_processed"] += 1
                self.save_tracking()
                
                print(f"Processed: {founder_name}")
            
            # Mark as complete when done
            self.tracking_data["conversion_status"] = "complete"
            self.save_tracking()

if __name__ == "__main__":
    # File paths
    input_json = "/Users/aveekgoyal/ice_breaker/agents/founders_wiki_data.json"
    output_csv = "/Users/aveekgoyal/ice_breaker/founders_wiki_data.csv"
    tracking_file = "/Users/aveekgoyal/ice_breaker/conversion_tracking.json"
    
    # Create and run converter
    converter = WikiDataConverter(input_json, output_csv, tracking_file)
    print(f"Found {converter.max_experiences} maximum experiences across all founders")
    converter.convert()
    
    print("\nConversion completed!")
    print(f"Total founders processed: {converter.tracking_data['total_founders_processed']}")
    print(f"Output CSV: {output_csv}")
