import os
from wyl.helpers import HelperClass

if not os.path.isdir("data"):
    os.mkdir("data")

if __name__ == '__main__':
    Helper = HelperClass(
        project_path=os.getcwd(),
        json_file="files.json",
        map_filename="map1.osm"
    )

    if not os.path.isfile(Helper.JSON_FILE):
        Helper.generate_files_json()
    else:
        Helper.fetch_missing_files()
