import filecmp
import operator
import os
from typing import List, Union, Set
import shutil
from tqdm import tqdm
import logging
import datetime

from photoarchiver.helpers.exif import get_file_metadata
from photoarchiver.helpers.file import get_digest, get_file_extension
from photoarchiver.helpers.path import get_deduplicated_destination_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileOperation:
    """A FileOperation is a container class describing the operations ran by the PhotoArchiver.
    These operations have a `source_path`, `destination_path` and a `creation_time`.

    This class is designed to be used in conjunction with a set for deduplication of files.
    """

    def __init__(self,
                 source_path: str,
                 destination_path: str,
                 creation_time: datetime.datetime):
        self.source_path = source_path
        self.destination_path = destination_path
        self.creation_time = creation_time
        self.file_hash = get_digest(source_path)

    def __eq__(self, obj):
        return isinstance(obj, FileOperation) and filecmp.cmp(self.source_path, obj.source_path)

    def __hash__(self):
        return self.file_hash

    def __iter__(self):
        return iter([self.source_path, self.destination_path])


class PhotoArchiver:
    """Provides the logic to execute a set of file operations to archive a set of files from a list or single
    `source_directory` into a `destination_directory`. Set `copy_files` to True if you are looking to copy the files,
    false to move them.
    """

    def __init__(self,
                 source_directories: Union[str, List[str]],
                 destination_directory: str,
                 copy_files: bool = True):
        self.source_directories = source_directories if isinstance(source_directories, list) else [source_directories]
        self.destination_directory = destination_directory
        self.copy_files = copy_files

    def run(self):
        logger.info("Running PhotoArchiver")
        file_operations = self._get_file_operations()
        self._execute_file_operations(file_operations)

    def _get_file_operations(self) -> Set:
        """Generates set of file operations

        The FileOperation deduplication logic works by using the `__hash__` and `__eq__` methods.

        File comparisons are usually expensive, so we let the set first compare files by hash and only
        use `__eq__` on the list of files with the same hash.
        """
        logger.info("Getting FileOperation objects")
        file_paths = self._get_file_paths()
        file_operations = [self._get_file_operation(file_path) for file_path in tqdm(file_paths)]

        # sort file operations to keep the repeated files with the lowest creation time.
        file_operations.sort(key=operator.attrgetter('creation_time'))
        file_operations = set(file_operations)

        duplicated_files_count = len(file_paths) - len(file_operations)
        if duplicated_files_count:
            logger.info(f"Identified {duplicated_files_count} duplicated files")

        return file_operations

    def _execute_file_operations(self, file_operations: Set[FileOperation]):
        operation_type = "Copying" if self.copy_files else "Moving"
        logger.info(f"{operation_type} files to {self.destination_directory}")
        for source_path, destination_path in tqdm(file_operations):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            destination_path = get_deduplicated_destination_path(destination_path)

            if self.copy_files:
                shutil.copy2(source_path, destination_path)
            else:
                shutil.move(source_path, destination_path)

    def _get_file_operation(self, file_path: str) -> FileOperation:
        file_metadata = get_file_metadata(file_path)
        file_extension = get_file_extension(file_path)
        creation_time = file_metadata['creation_time']
        file_directory = f"{creation_time:%Y/%-m - %B - Week %V}"

        # create new file name
        time_string = f"{creation_time:%Y-%b-%d %H-%M-%S}"
        location_string = "-".join(filter(None, [file_metadata.get("location").get(k).replace(" ", "")
                                                 for k in ["cc", "name"] if file_metadata.get("location")]))

        new_file_name = "-".join(filter(None, [time_string, location_string])) + file_extension
        destination_path = os.path.join(self.destination_directory, file_directory, new_file_name)

        return FileOperation(
            source_path=file_path,
            destination_path=destination_path,
            creation_time=creation_time
        )

    def _get_file_paths(self):
        return [os.path.join(dp, f)
                for source_directory in self.source_directories
                for dp, dn, filenames in os.walk(source_directory)
                for f in filenames]
