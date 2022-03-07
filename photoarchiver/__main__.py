import sys
import argparse

from photoarchiver.photoarchiver import PhotoArchiver


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Sort files by date using file metadata.')
    parser.add_argument('--source-directory-list', nargs='+',
                        help='Source directories to get files recursively from.',
                        required=True)
    parser.add_argument('--destination-directory', type=str, help='Destination directory', required=True)
    parser.add_argument('--move-files', action='store_true',
                        help='If True, files are copied. Otherwise, files are moved.',
                        default=False)

    args = parser.parse_args()

    photo_archiver = PhotoArchiver(source_directories=args.source_directory_list,
                                   destination_directory=args.destination_directory,
                                   copy_files=not args.move_files)
    photo_archiver.run()


if __name__ == '__main__':
    sys.exit(main())
