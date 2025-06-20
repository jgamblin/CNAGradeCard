import os
import requests
import json
from datetime import datetime, timedelta

def get_cna_list():
    """
    Downloads the master CNA list.
    """
    url = "https://raw.githubusercontent.com/CVEProject/cve-website/dev/src/assets/data/CNAsList.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading CNA list: {e}")
        return None

def get_cve_records():
    """
    Reads CVE records from the local cve_data directory and filters them for the last 6 months.
    Assumes the repository is already cloned and up-to-date.
    """
    # Path to the data directory, which is mapped from the host
    clone_path = os.path.join(os.path.dirname(__file__), '..', 'cve_data')

    if not os.path.exists(clone_path):
        print(f"Error: CVE data directory not found at {clone_path}")
        print("Please run the build_and_test.sh script to clone the data first.")
        return []

    print("Filtering records from local CVE data...")
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_cves = []
    cves_path = os.path.join(clone_path, 'cves')

    for root, _, files in os.walk(cves_path):
        for file in files:
            if file.startswith('CVE-') and file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    try:
                        cve_data = json.load(f)
                        date_published_str = cve_data.get('cveMetadata', {}).get('datePublished')
                        if date_published_str:
                            date_published = datetime.fromisoformat(date_published_str.replace('Z', '+00:00'))
                            if date_published.replace(tzinfo=None) >= six_months_ago:
                                recent_cves.append(cve_data)
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

    print(f"Found {len(recent_cves)} recent CVEs.")
    return recent_cves

if __name__ == '__main__':
    cna_list = get_cna_list()
    if cna_list:
        print(f"Successfully downloaded {len(cna_list)} CNA records.")
    
    cve_records = get_cve_records()
    # You can add further processing here if needed
