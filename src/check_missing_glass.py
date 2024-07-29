import os
import csv
import pandas as pd

def check_missing_years(base_path):
    results = []
    sites = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    total_sites = len(sites)
    
    print(f"Total sites to check: {total_sites}")

    for i, site in enumerate(sites, 1):
        print(f"Checking site {i}/{total_sites}: {site}")
        site_path = os.path.join(base_path, site)
        for year in range(2002, 2022):  # 2002 to 2021 inclusive
            year_path = os.path.join(site_path, str(year))
            if not os.path.isdir(year_path):
                results.append((site, year, 0))
            else:
                file_count = sum(1 for f in os.listdir(year_path) if f.endswith('_geographic.tif'))
                if file_count != 46:
                    results.append((site, year, file_count))
        
        # Print progress every 10 sites
        if i % 10 == 0 or i == total_sites:
            print(f"Processed {i}/{total_sites} sites")
    
    return results

def write_results_to_file(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Site', 'Year', 'File Count'])
        writer.writerows(results)

if __name__ == "__main__":
    base_path = "/home/hamid/mnt/nas/Hamid/GLASS/EC_SITES"
    missing_years_file = "incomplete_years_GLASS.csv"
    
    print("Checking for missing and incomplete years...")
    missing_data = check_missing_years(base_path)
    
    write_results_to_file(missing_data, missing_years_file)
    print(f"Missing and incomplete years written to {missing_years_file}")
    
    total_missing = len(missing_data)
    print(f"Total missing or incomplete entries: {total_missing}")

    # Print summary of missing data
    site_year_counts = {}
    for site, year, count in missing_data:
        if site not in site_year_counts:
            site_year_counts[site] = 0
        site_year_counts[site] += 1

    print("\nSummary of missing or incomplete data:")
    for site, count in site_year_counts.items():
        print(f"{site}: {count} year(s) missing or incomplete")

# Run this script with: python check_missing_glass.py