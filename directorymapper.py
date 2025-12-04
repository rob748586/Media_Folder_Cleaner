from pathlib import Path

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