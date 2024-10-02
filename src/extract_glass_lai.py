import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from datetime import datetime
import xarray as xr
import rioxarray
from tqdm import tqdm
import multiprocessing as mp

def process_site(site_info):
    i, name, lat, lon = site_info
    print(f"Processing: {name}, i: {i}")

    base_dir = "/Users/hdashti/mnt/nas/GLASS/EC_SITES/"
    years = np.arange(2002, 2022)
    fnames = []
    dates = []

    for year in years:
        dir_path = os.path.join(base_dir, name, str(year))
        tif_files = glob.glob(dir_path + "/*.tif")
        # Check if number of files is exactly 46
        if len(tif_files) == 46:
            for file in tif_files:
                fnames.append(file)
                date_part = file.split("/")[-1].split(".")[2][1:]
                dates.append(datetime.strptime(date_part, "%Y%j").date())
        else:
            print(f"Warning: {dir_path} does not contain exactly 46 files.")

    lai_tmp = []
    for fname in tqdm(fnames, desc=f"Processing {name}", unit="file"):
        date = dates[fnames.index(fname)]
        da = rioxarray.open_rasterio(fname).squeeze().drop("band")
        da = da.expand_dims(time=[date])
        lai_tmp.append(da.sel(x=lon, y=lat, method="nearest").values * 0.1)

    data_frame = pd.DataFrame(lai_tmp, index=dates, columns=["LAI"])
    output_dir = "/Users/hdashti/mnt/nas/GLASS/csv_files/"
    data_frame.to_csv(f"{output_dir}{name}.csv")


if __name__ == "__main__":
    # merged_coords_1 = pd.read_csv("../data/merged_coords_batch1.csv")
    # merged_coords_2 = pd.read_csv("../data/merged_coords_batch2.csv")
    # merged_coords = pd.concat([merged_coords_1, merged_coords_2], ignore_index=True)
    merged_coords = pd.read_csv("./ICOS_fluxnet_coords.csv")

    # Prepare the list of arguments for each site
    site_info_list = [
        (i, merged_coords["name"][i], merged_coords["Lat"][i], merged_coords["Lon"][i])
        for i in range(merged_coords.shape[0])
    ]

    # Get the number of CPU cores
    num_cores = os.cpu_count()

    # Create a pool of workers and map the process_site function to all sites in parallel
    with mp.Pool(processes=num_cores) as pool:
        list(
            tqdm(
                pool.imap(process_site, site_info_list),
                total=len(site_info_list),
                desc="Overall Progress",
            )
        )