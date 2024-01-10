def reprojection_fun(root, outpath, file):
    import os
    import h5py
    from utils import filter_qa, implement_reprojection, merge_tif, remove_files

    field_list = [
        "01_LAI",
        "02_SLAI",
        "03_FPAR",
        "05_NDVI",
        "07_SZA",
        "08_VZA",
        "09_SAA",
        "10_VAA",
        "11_DASF",
        "12_ERTI",
        "13_W443",
        "14_W551",
        "15_W680",
        "16_W780",
    ]

    field_list = field_list[0:3]

    implement_reprojection(root, file, outpath, field_list)
    h5fpath = os.path.join(root, file)
    h5f = h5py.File(h5fpath, "r")
    date = file.split("_")[5]
    tile_list = [key for key in h5f.keys()]

    for tile in tile_list:
        input_files = []
        field_names = []
        if tile != "tile20" and tile != "tile21":
            for i in range(len(field_list)):
                input_files.append(
                    outpath + field_list[i] + "_" + str(date) + "_" + tile + ".tif"
                )
                field_names.append(field_list[i][3:])
            output_file = outpath + tile + "_" + str(date) + ".tif"
            merge_tif(input_files, field_names, output_file)
            remove_files(input_files)
        else:
            input_files_Asia = []
            input_files_US = []
            field_names = []
            for i in range(len(field_list)):
                input_files_Asia.append(
                    outpath + field_list[i] + "_" + str(date) + "_" + tile + "_Asia.tif"
                )
                input_files_US.append(
                    outpath + field_list[i] + "_" + str(date) + "_" + tile + "_US.tif"
                )
                field_names.append(field_list[i][3:])
            output_file_Asia = outpath + tile + "_" + str(date) + "_Asia.tif"
            output_file_US = outpath + tile + "_" + str(date) + "_US.tif"
            merge_tif(input_files_Asia, field_names, output_file_Asia)
            merge_tif(input_files_US, field_names, output_file_US)
            remove_files(input_files_Asia)
            remove_files(input_files_US)


root_path = ""
out_path = r"./outputs/"
# file = "DSCOVR_EPIC_L2_VESDR_02_20160823152458_03.h5"
# reprojection_fun(root,outpath,file)

# Shell input
import sys

hdf5_file = sys.argv[1]
reprojection_fun(root_path,out_path,hdf5_file)