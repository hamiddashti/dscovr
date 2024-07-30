import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import xarray as xr
import rioxarray
import dask
from dask.distributed import Client, progress, wait
from tqdm.auto import tqdm

# Function to process each file
def process_file(fname, date):
    da = rioxarray.open_rasterio(fname, chunks={"x": 1000, "y": 1000})
    da = da.squeeze().drop("band")  # Remove the band dimension if it exists
    da = da.expand_dims(time=[date])  # Add time dimension
    return da

# Function to process each site
def process_site(name, lat, lon, base_dir, output_dir):
    print(f"Processing site {name}")
    years = np.arange(2002, 2022)
    fnames = []
    dates = []

    for year in years:
        dir_path = os.path.join(base_dir, name, str(year))
        tif_files = glob.glob(dir_path + "/*.tif")
        for file in tif_files:
            fnames.append(file)
            date_part = file.split("/")[-1].split(".")[2][1:]
            dates.append(datetime.strptime(date_part, "%Y%j").date())

    # Create a list of delayed objects
    delayed_arrays = [
        dask.delayed(process_file)(fname, date) for fname, date in zip(fnames, dates)
    ]

    # Compute all delayed objects in parallel
    data_arrays = dask.compute(*delayed_arrays)
    
    combined_da = xr.concat(data_arrays, dim="time")
    combined_da.attrs["site_name"] = name
    combined_da.attrs["latitude"] = lat
    combined_da.attrs["longitude"] = lon
    
    ds = combined_da.to_dataset(name="glass_lai")
    chunks = {"time": 1, "y": 1000, "x": 1000}  # Adjust chunk sizes as needed
    ds = ds.chunk(chunks)
    ds["time"] = pd.to_datetime(ds["time"])
    
    output_file = os.path.join(output_dir, f"{name}_GLASS_LAI_2002_2021.zarr")
    write_job = ds.to_zarr(output_file, mode="w", compute=False)
    
    return write_job, output_file

# Main execution
if __name__ == "__main__":
    # Set up Dask client
    client = Client()
    
    merged_coords_1 = pd.read_csv("./merged_coords_batch1.csv")
    merged_coords_2 = pd.read_csv("./merged_coords_batch2.csv")
    merged_coords = pd.concat([merged_coords_1, merged_coords_2], ignore_index=True)

    base_dir = "/Users/hdashti/NAS/Hamid/GLASS/EC_SITES/"
    output_dir = "/Users/hdashti/NAS/Hamid/GLASS/xr_files/"

    # Process all sites in parallel
    futures = []
    for i in range(len(merged_coords)):
        name = merged_coords["name"][i]
        lat = merged_coords["Lat"][i]
        lon = merged_coords["Lon"][i]
        future = client.submit(process_site, name, lat, lon, base_dir, output_dir)
        futures.append(future)

    # Wait for all computations to finish and show progress
    progress(futures)
    results = client.gather(futures)

    # Write results to Zarr files
    for write_job, output_file in results:
        print(f"Writing to Zarr file: {output_file}")
        future = client.compute(write_job)
        progress(future)
        future.result()
        print(f"File saved as {output_file}")

    client.close()