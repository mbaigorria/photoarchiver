import os
import json
import hashlib
import requests
from typing import Optional, Dict


def get_digest(file_path) -> int:
    # Based on https://stackoverflow.com/a/55542529
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return int(h.hexdigest(), 16)


def get_magic_numbers() -> Dict:
    magic_url = "https://gist.githubusercontent.com/qti3e/6341245314bf3513abb080677cd1c93b/raw/" \
                "80d7838ba189849e492a4f5f3da88c84390c1250/extensions.json"
    url = requests.get(magic_url)
    return json.loads(url.text)


_MAGIC_NUMBERS = get_magic_numbers()


def get_file_extension(file_path: str) -> str:
    file_extension = os.path.splitext(file_path)[-1].lower().strip()
    force_search = any([s in file_extension for s in ('\\', ':')])

    if not file_extension or force_search:
        file_type = get_file_type_with_magic_strings(file_path)
        if file_type is not None:
            file_extension = f".{file_type}"

    return file_extension


def get_file_type_with_magic_strings(file_path: str) -> Optional[str]:
    max_read_size = 520  # this covers most of the file types, except some like iso

    with open(file_path, 'rb') as fd:
        file_head = fd.read(max_read_size)

        for ext, type_info in _MAGIC_NUMBERS.items():
            for byte_offset, magic_number in map(lambda s: s.split(","), type_info["signs"]):
                magic_number = bytearray.fromhex(magic_number)
                if file_head[int(byte_offset):].startswith(magic_number):
                    return ext

    return None
