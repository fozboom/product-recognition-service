"""
Script for counting the number of processed sites in the annotation JSON file.
A site is considered processed if it has at least one entity with valid start and end positions.
"""

import json
import sys
from pathlib import Path


def count_processed_sites(json_file_path):
    """
    Counts the number of processed sites in the JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file
        
    Returns:
        tuple: (total_sites, processed_sites, percentage_processed)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error reading JSON: {e}")
        return None
    
    total_sites = 0
    processed_sites = 0
    
    # Check if data is a list or a dictionary
    if isinstance(data, list):
        sites_data = data
    elif isinstance(data, dict):
        # If it's a dictionary, we look for a key that might contain a list of sites
        if 'sites' in data:
            sites_data = data['sites']
        elif 'data' in data:
            sites_data = data['data']
        else:
            # If the structure is unclear, we try to use the entire dictionary as one element
            sites_data = [data]
    else:
        print("Unexpected data structure in JSON file")
        return None
    
    for site in sites_data:
        total_sites += 1
        
        # Check for the presence of entities
        if 'entities' in site and isinstance(site['entities'], list):
            # Check if there is at least one valid entity
            has_valid_entity = False
            
            for entity in site['entities']:
                if isinstance(entity, dict):
                    # Check if start and end exist and are not equal to 0
                    # or if there is a non-empty text
                    start = entity.get('start', 0)
                    end = entity.get('end', 0)
                    text = entity.get('text', '')
                    
                    # A site is considered processed if:
                    # 1. start and end are not equal to 0 simultaneously, OR
                    # 2. there is a non-empty text
                    if (start != 0 or end != 0) or (text and text.strip()):
                        has_valid_entity = True
                        break
            
            if has_valid_entity:
                processed_sites += 1
    
    percentage = (processed_sites / total_sites * 100) if total_sites > 0 else 0
    
    return total_sites, processed_sites, percentage


def main():
    json_file = Path(__file__).resolve().parents[1] / "data" / "processed" / "labeled_data.json"
    
    if not Path(json_file).exists():
        print(f"File {json_file} not found in the current directory")
        sys.exit(1)
    
    print(f"Analyzing file: {json_file}")
    print("=" * 50)
    
    result = count_processed_sites(json_file)
    
    if result is None:
        sys.exit(1)
    
    total, processed, percentage = result
    
    print(f"Total number of sites: {total}")
    print(f"Processed sites: {processed}")
    print(f"Unprocessed sites: {total - processed}")
    print(f"Percentage of processed sites: {percentage:.2f}%")
    
    if total > 0:
        print("\n" + "=" * 50)
        print("STATISTICS:")
        print(f"Processed: {processed}/{total} ({percentage:.1f}%)")
        print(f"Unprocessed: {total - processed} ({100-percentage:.1f}%)")


if __name__ == "__main__":
    main() 