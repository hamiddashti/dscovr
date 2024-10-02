import logging
import time
from pyproj import Proj, transform
import math
import requests
from bs4 import BeautifulSoup
import os
import h5py
from pyhdf.SD import SD, SDC
from osgeo import gdal, osr
import warnings
import pandas as pd
import concurrent.futures

warnings.simplefilter(action="ignore", category=FutureWarning)

# Set up logging

logging.basicConfig(filename='script_log_missing_files.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def latlon_to_modis_tile(lat, lon):
    # MODIS Sinusoidal Projection
    modis_sinu = Proj("+proj=sinu +R=6371007.181 +nadgrids=@null +wktext")
    wgs84 = Proj(proj="latlong", datum="WGS84")

    # Convert lat/lon to MODIS Sinusoidal coordinates
    x, y = transform(wgs84, modis_sinu, lon, lat)

    # MODIS Grid specifics
    tile_size_meters = 1111950.5196666666  # Size of each MODIS tile in meters
    x_origin = -20015109.354  # Westernmost coordinate
    y_origin = 10007554.677  # Northernmost coordinate

    h = int((x - x_origin) / tile_size_meters)
    v = int((y_origin - y) / tile_size_meters)

    return h, v

def generate_filename(lat, lon, template="GLASS01E01.V60.A2002001.h00v08.2022010.hdf"):
    h, v = latlon_to_modis_tile(lat, lon)
    hv_str = f"h{h:02d}v{v:02d}"
    filename = template.replace("h00v08", hv_str)
    return filename

def get_hdf_files(url, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            hdf_files = [
                a["href"]
                for a in soup.find_all("a", href=True)
                if a["href"].endswith(".hdf")
            ]
            return hdf_files
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logging.error(f"Failed to retrieve the webpage after {max_retries} attempts: {url}")
                return []

def filter_files_by_tile(hdf_files, h, v):
    hv_str = f"h{h:02d}v{v:02d}"
    filtered_files = [file for file in hdf_files if hv_str in file]
    return filtered_files

def download_file(url, file_name, output_directory, max_retries=3, delay=5):
    file_url = url + file_name
    for attempt in range(max_retries):
        try:
            response = requests.get(file_url, stream=True, timeout=30)
            response.raise_for_status()
            file_path = os.path.join(output_directory, file_name)
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            # logging.info(f"Downloaded file: {file_path}")
            return
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logging.error(f"Failed to download file after {max_retries} attempts: {file_url}")

def inspect_hdf_file(file_path):
    with h5py.File(file_path, "r") as file:
        # List all groups
        print("Keys: %s" % file.keys())
        for key in file.keys():
            print(f"\nContent in '{key}':")
            data = file[key]
            print(data)
            if isinstance(data, h5py.Dataset):
                print(f"Dataset '{key}' shape: {data.shape}")
                print(f"Dataset '{key}' dtype: {data.dtype}")
                print(data[:])
            elif isinstance(data, h5py.Group):
                print(f"Group '{key}' contains: {list(data.keys())}")

def get_directories(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the response text with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all the <a> tags and get their href attributes
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Filter out the links that don't represent directories
        directories = [link for link in links if link.endswith("/")]

        return directories
    except Exception as e:
        logging.error(f"Error in get_directories: {e}")
        return []

def convert_projection(file_path):
    try:
        # Access the LAI_500M subdataset
        lai_sds_path = 'HDF4_EOS:EOS_GRID:"' + file_path + '":GLASS01E01:LAI_500M'
        lai_sds_ds = gdal.Open(lai_sds_path, gdal.GA_ReadOnly)

        # Create a new geotransform and spatial reference for the geographic projection
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)  # WGS84

        # Create the output filename
        output_file = os.path.splitext(file_path)[0] + "_geographic.tif"

        # Use gdal.Warp to convert the projection
        gdal.Warp(output_file, lai_sds_ds, dstSRS=srs)

        # logging.info(f"File saved at: {output_file}")
    except Exception as e:
        logging.error(f"Error in convert_projection: {e}")



def process_site(name, lat, lon, base_url):
    for year in range(2002, 2022):
        output_directory = f"/home/hamid/mnt/nas/Hamid/GLASS/EC_SITES/{name}/{str(year)}"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        # Check if the directory is empty or has less than 46 files
        existing_files = [f for f in os.listdir(output_directory) if f.endswith('_geographic.tif')]
        if len(existing_files) == 46:
            logging.info(f"Skipping {name} for year {year} - already complete")
            continue
        
        directories = get_directories(base_url + str(year) + "/")
        for j in range(1, len(directories)):
            url = base_url + str(year) + "/" + directories[j]
            h, v = latlon_to_modis_tile(lat, lon)
            logging.info(f"Processing: name {name}, year {year}, directory {directories[j]}")
            hdf_files = get_hdf_files(url)
            filtered_files = filter_files_by_tile(hdf_files, h, v)
            if filtered_files:
                file_to_download = filtered_files[0]
                download_file(url, file_to_download, output_directory)
                file_path = f"{output_directory}/{filtered_files[0]}"
                convert_projection(file_path)
                os.remove(file_path)
            else:
                logging.warning(f"No .hdf files found for MODIS, name {name}, year {year}, directory {directories[j]}.")

# Main execution
if __name__ == "__main__":
    try:
        # Merge the two CSV files
        merged_coords_1 = pd.read_csv("../data/merged_coords_batch1.csv")
        merged_coords_2 = pd.read_csv("../data/merged_coords_batch2.csv")
        merged_coords = pd.concat([merged_coords_1, merged_coords_2], ignore_index=True)

        base_url = "http://www.glass.umd.edu/LAI/MODIS/500m/"
        skipped_sites_file = "/home/hamid/mnt/nas/Hamid/GLASS/EC_SITES/skipped_sites_missing.txt"

        # Prepare lists for sites with missing files
        sites_to_process = []

        # Iterate over sites and check for missing files
        for i in range(len(merged_coords)):
            name = merged_coords["name"][i]
            lat = merged_coords["Lat"][i]
            lon = merged_coords["Lon"][i]
            for year in range(2002, 2022):
                output_directory = f"/home/hamid/mnt/nas/Hamid/GLASS/EC_SITES/{name}/{str(year)}"
                if not os.path.exists(output_directory):
                    sites_to_process.append((name, lat, lon))
                    break
                else:
                    existing_files = [f for f in os.listdir(output_directory) if f.endswith('_geographic.tif')]
                    if len(existing_files) < 46:
                        sites_to_process.append((name, lat, lon))
                        break

        # Run in parallel with limited concurrency
        max_workers = 24  # Adjust this number based on your system's capabilities
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_site, site[0], site[1], site[2], base_url) for site in sites_to_process]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in thread: {e}")

    except Exception as e:
        logging.error(f"Main execution error: {e}")

logging.info("Script completed.")

# command to run the script
#nohup python download_glass_missing_files.py > output_missing.log 2>&1 &