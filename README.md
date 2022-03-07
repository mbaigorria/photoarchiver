# Photo Archiver
Simple photo archiver to organize file dumps into a date based tree directory structure using file metadata. File
metadata is used to try and identify the creation date of the file. We also use an EXIF reader to find the GPS
coordinates of where the file was created and add some location metadata to the filenames when possible.

![alt text](https://github.com/mbaigorria/photoarchiver/raw/main/example.png)

## User installation

The easiest way to install `photoarchiver` is using pip:
```
pip install photoarchiver
```

## Usage

To see all options:
```
photoarchiver -h
```

To run on a source and output directory:
```
photoarchiver --source-directory-list <source_directory_1> <source_directory_2> --destination-directory <destination_directory>
```

If you want to move rather than copy the files, use the flag `--move-files`.