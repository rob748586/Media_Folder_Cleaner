import os
import argparse
from pathlib import Path
from shutil import copyfile
from exif import Image

# Creates a one to many mapping of filenames and dirctories to ensure duplicates are only copied once.
# naieve implementation - does not compare files using diff or hash currently.
class DirectoryMapper:
    file_path_dictionary = {}

    # enumerates a directory storing all file names in the dictionary files_dictionary, using the filename as the key an the path as value.
    # optionally enumerates directory structure recursively (including subfolders).
    def map_directory(self, path, parse_recursively : bool = False):
        for item in path.iterdir():
            if item.is_dir() and parse_recursively:
                self.map_directory(Path.joinpath(path, item), parse_recursively)
            else:
                # item is first instance of a file name, so create a list with a single path.
                if self.file_path_dictionary.get(item.name) == None:
                    self.file_path_dictionary[item.name] = [path]
                else:
                # item is a duplicate file name, so add the new path to the end of the list.
                    self.file_path_dictionary[item.name].append(path)

    def display_results(self):
        # display total count number of unique file names in dictionary.
        print (len(self.file_path_dictionary.keys()), "unique files")

        # count and display number of duplicate files in dictionary.
        count = 0
        for filename in self.file_path_dictionary:
            if len(self.file_path_dictionary[filename]) > 1:
                count += len(self.file_path_dictionary[filename]) - 1

        print (count, "files with duplicates.")

    def get_file_paths(self):
        output_paths = []
        
        for filename, paths in self.file_path_dictionary.items():
            for path in paths:
                absolute_path = path / filename
                output_paths.append(absolute_path)
        
        return output_paths

# create a path in the format /inputpath/YYYY/MM where YYYY is the Year and MM is the numerical month
# from the exif data, and create the folders if they do not already exist.
# returns the updated destination_path including the suffix, or the unaltered destination_path if image exif data is not available.
def add_date_suffix_to_path_from_image_exif_and_create_paths(image_path, file_type, destination_path):
    initial_path = destination_path
    
    with open(image_path, "rb") as file:
        try:
            # load image
            image = Image(file)

            if image.has_exif:
                # query exif data for date time
                date = image.datetime.split(" ")[0]
                date_array = date.split(":")
                year = date_array[0]
                month = date_array[1]                

                # create subfolder for year if it doesn't exist
                destination_path = Path.joinpath(destination_path, year + "/")

                if not destination_path.exists():
                    os.mkdir(str(destination_path))

                # create subfolder for month if it doesn't exist
                destination_path = Path.joinpath(destination_path, month + "/")
                                                
                if not destination_path.exists():
                    os.mkdir(str(destination_path))
        except:
            # if any errors arise from bad image data or exif data, return the unmodified path.
            destination_path = initial_path

    return destination_path

def copy_unique_files_to_destination(output_path, input_paths, file_types):
    for source_path in input_paths:
            # iterate through the accepted file types dictionary
            for file_type in file_types:
                
                # iterate through each acceptable extension for a given file type.
                for extension in file_types[file_type]:
                    if str(str(source_path).lower()).endswith(extension):

                        # append output path with the sub folder according to file type (image, movie, etc...)
                        destination_path = Path.joinpath(output_path, file_type)

                        if not Path.exists(destination_path):
                            os.mkdir(str(destination_path))

                        filename = source_path.name

                        # if the file is an image exif data is used to append further subfolders according to year and month image was created.
                        if file_type == "Images":
                            destination_path = add_date_suffix_to_path_from_image_exif_and_create_paths(source_path, file_type, destination_path)
                        
                        # append filename to destination path.
                        destination_path = Path.joinpath(destination_path,filename)
                                        
                        # copy file if it does not exist.
                        if not Path(destination_path).exists():
                            copyfile (str(source_path), str(destination_path))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sourcefolder")
    parser.add_argument("destinationfolder")
    args = parser.parse_args()
    
    # input directory containing unsorted files with duplicates to parse
    input_path = Path(args.sourcefolder)
    
    output_path = Path(args.destinationfolder)

    if input_path.exists() and output_path.exists():
        mapper = DirectoryMapper()

        # enumerate the folder in path, adding all files recursively to the files_dictionary object.
        mapper.map_directory(input_path, True)

        # output number of files and total number of duplicates to console.
        mapper.display_results()

        paths = mapper.get_file_paths()

        # accepted file types. key will be used as a subfolder when copying files.
        file_types = {"Images" : {".jpg", ".jpeg", ".png", ".gif"},
                    "Videos" : {".mp4", ".mov"}}

        copy_unique_files_to_destination(output_path, paths, file_types)

main()

