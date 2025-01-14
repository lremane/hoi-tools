import os

def rename_files_in_directory(directory, rename_to):
    # Get a list of all files in the directory
    files = os.listdir(directory)

    for file in files:
        new_name = f"{rename_to}_{file}"
        # Get the full path of the old and new filenames
        old_path = os.path.join(directory, file)
        new_path = os.path.join(directory, new_name)
        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed: {file} -> {new_name}")

directory_path = "hico_new/images/train2015"
rename_to = 'train2015'
# Call the function to rename the files
rename_files_in_directory(directory_path, rename_to)
