import json
import os
import re
import shutil
import sys
import threading
import time
import xml.etree.ElementTree as ElementTree


class HelperClass(object):
    JSON_FILE = "files.json"
    MAP_FILE = "map.osm"
    DEBUG = False
    PROJECT_PATH = r"C:\Users\sasch\PycharmProjects\pythonProject_get_hgt"

    def __init__(self, json_file=None, map_file=None, project_path=None, map_filename=None):
        if map_filename is not None:
            self.map_filename = map_filename

        if project_path is not None:
            self.PROJECT_PATH = project_path
        if json_file is not None:
            self.JSON_FILE = os.path.join(os.getcwd(), "data", "json", json_file)
        if map_file is not None:
            self.MAP_FILE = map_file

    class GatherFiles(threading.Thread):
        running = True
        files = []
        finished = False
        path = None

        def __init__(self, directory_path=None):
            if directory_path is not None:
                self.path = directory_path
            else:
                self.path = os.path.join("B:", "backups", "renderaccount", "data", "hgt")
            super(self.GatherFiles, self).__init__()

        def run(self) -> None:
            self.files = os.listdir(self.path)
            self.finished = True

    class RunSpinner(object):
        running = True
        run = None

        def __init__(self):
            self.spinner = self.spinning_cursor()
            self.run = threading.Thread(target=self.run_spinner)
            self.run.start()

        @staticmethod
        def spinning_cursor():
            while True:
                for cursor in '|/-\\':
                    yield cursor

        def run_spinner(self):
            try:
                while self.running:
                    sys.stdout.write(next(self.spinner) + " gathering")
                    sys.stdout.flush()
                    time.sleep(0.1)
                    sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b')
            except KeyboardInterrupt:
                print("\n - stopped by kb")

    @staticmethod
    def get_prefix(lat, lon):
        if lat > 0:
            a = "N"
        else:
            a = "S"
        if lon > 0:
            b = "E"
        else:
            b = "W"
        return a, b

    @staticmethod
    def extract_bounds(filepath):

        """
        extracts attribute-values from xml-file (filepath)
         e.g.
        
        <?xml version="1.0" encoding="UTF-8"?>
        <osm version="0.6" ...
            <bounds minlat="38.0300000" minlon="-80.4838000" maxlat="39.0463000" maxlon="-80.4595000"/>
                             """"""               """"""              """"""               """"""
                              lat(min)             lon(min)            lat(max)             lon(max)
        """

        root = ElementTree.parse(filepath).getroot()
        tag_attribute_names = ["minlat", "minlon", "maxlat", "maxlon"]
        attributes = {}
        for type_tag in root.findall('bounds'):
            for attribute_name in tag_attribute_names:
                attributes[attribute_name] = float(type_tag.get(attribute_name))

        min_lat = attributes["minlat"]
        min_lon = attributes["minlon"]
        max_lat = attributes["maxlat"]
        max_lon = attributes["maxlon"]

        return min_lat, min_lon, max_lat, max_lon

    @staticmethod
    def value_prepend_to_str(value):
        return "0" + str(int(value))

    def fetch_missing_files(self):
        filename_expected = ""
        json_ = json.load(open(self.JSON_FILE))
        self.MAP_FILE = os.path.join(os.path.join(self.PROJECT_PATH, "data", "maps"), self.map_filename)

        if not os.path.isfile(self.MAP_FILE):
            print("no map file: "+os.path.basename(self.MAP_FILE))
            sys.exit(1)

        min_lat, min_lon, max_lat, max_lon = self.extract_bounds(self.MAP_FILE)
        lat_prefix, lon_prefix = self.get_prefix(min_lat, min_lon)

        if max_lon < 0:
            max_lon = max_lon * -1
        if min_lon < 0:
            min_lon = min_lon * -1

        files_ = []
        if int(min_lon) < int(max_lon):
            for lon_ in range(int(min_lon), int(max_lon) + 1):
                min_lon_tmp = self.value_prepend_to_str(lon_)
                filename_expected = lat_prefix + str(int(min_lat)) + lon_prefix + min_lon_tmp + ".hgt"
                if filename_expected not in files_:
                    files_.append(filename_expected)

        if int(min_lat) < int(max_lat):
            for lat_ in range(int(min_lat), int(max_lat) + 1):
                min_lon_tmp = self.value_prepend_to_str(min_lon)
                filename_expected = lat_prefix + str(lat_) + lon_prefix + str(min_lon_tmp) + ".hgt"
                if filename_expected not in files_:
                    files_.append(filename_expected)

        done = False

        if len(files_) > 0:
            for file_ in files_:
                if filename_expected not in os.listdir(
                        os.path.join(self.PROJECT_PATH, "data", "hgt")
                ):
                    print(" < not local")
                    for f in json_["files"]:
                        if f["filename"] == file_:
                            shutil.copy(os.path.join(json_["base_path"], f["filename"]),
                                        os.path.join(self.PROJECT_PATH, "data", "hgt",
                                                     f["filename"]))
                            print(" - copied " + os.path.join(json_["base_path"], f["filename"]))
                done = True

        if done:
            sys.exit(0)

        if int(min_lon) == int(max_lon):

            min_lon_tmp = self.value_prepend_to_str(min_lon)
            filename_expected = lat_prefix + str(int(min_lat)) + lon_prefix + min_lon_tmp + ".hgt"

            if filename_expected not in os.listdir(os.path.join(self.PROJECT_PATH, "data")):
                if os.path.isdir(json_["base_path"]):
                    for f in json_["files"]:
                        if filename_expected == f["filename"]:
                            shutil.copy(os.path.join(json_["base_path"], f["filename"]),
                                        os.path.join(self.PROJECT_PATH, "data", "hgt", f["filename"]))
                            print(" - copied " + os.path.join(json_["base_path"], f["filename"]))

            else:
                if self.DEBUG:
                    filepath_ = os.path.join(self.PROJECT_PATH, "data", "hgt", filename_expected)
                    print(
                        "> file already copied ['" + filepath_ + "']"
                    )

    def generate_files_json(self):
        file_index = 0
        g_ = self.GatherFiles()
        g_.start()

        r = self.RunSpinner()
        while not g_.finished:
            time.sleep(1)
        r.running = False

        print("")
        print(str(len(g_.files)) + " files found")
        print(" ----- ")

        folders_ = []
        extensions_ = []
        no_match = []
        f_count = 0
        f_added = []

        files_collected = {
            "base_path": g_.path.replace(":", ":\\"),
            "files": []
        }

        for filename in g_.files:
            if not os.path.isfile(os.path.join(g_.path, filename)):
                folders_.append(os.path.dirname(os.path.join(g_.path, filename)))
            else:
                m = re.search(r"^(\w)(\d+)(\w)(\d+)", filename.split(".")[-2], re.DOTALL)
                if m is not None:
                    if filename not in f_added:
                        files_collected["files"].append({
                            "file_index": file_index,
                            "filename": filename,
                            "filesize": os.stat(os.path.join(g_.path, filename)).st_size,
                            "file_mtime": os.stat(os.path.join(g_.path, filename)).st_mtime
                        })
                        f_added.append(filename)
                    file_index += 1
                    print("+" + str(len(files_collected["files"])))
                else:
                    no_match.append(filename)
                if filename.split(".")[-1] not in extensions_:
                    extensions_.append(filename.split(".")[-1])
            f_count += 1
        files_collected["extensions"] = extensions_

        with open(self.JSON_FILE, "w") as json_file:
            json_file.write(json.dumps(files_collected))
            json_file.close()
