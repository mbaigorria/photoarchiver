from typing import Tuple, Dict

import exifread
from datetime import datetime
import os
import reverse_geocoder as rg

Coordinates = Tuple[float, float]
_LOCATION_CACHE = {}


# based on: https://gist.github.com/snakeye/fdc372dbf11370fe29eb

def get_exif_tags(file_path: str) -> Dict:
    with open(file_path, 'rb') as f:
        exif_tags = exifread.process_file(f)

    return exif_tags


def get_file_metadata(file_path: str) -> Dict:
    exif_tags = get_exif_tags(file_path)

    creation_time = get_creation_time(file_path)
    creation_time_from_exif = get_exif_creation(exif_tags)
    location = get_exif_location(exif_tags)

    if creation_time_from_exif is not None:
        creation_time = min(creation_time, creation_time_from_exif)

    return {
        "creation_time": creation_time,
        "location": location
    }


def get_creation_time(file_path: str) -> datetime:
    return min(datetime.utcfromtimestamp(os.path.getctime(file_path)),
               datetime.utcfromtimestamp(os.path.getmtime(file_path)))


def _convert_to_degress(value: exifread.utils.Ratio) -> float:
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degrees in float format
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)


def get_exif_location_coordinates(exif_data: Dict) -> Coordinates:
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    gps_latitude = exif_data.get('GPS GPSLatitude')
    gps_latitude_ref = exif_data.get('GPS GPSLatitudeRef')
    gps_longitude = exif_data.get('GPS GPSLongitude')
    gps_longitude_ref = exif_data.get('GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    return lat, lon


def get_exif_location(exif_data: Dict) -> Dict:
    location_coordinates = get_exif_location_coordinates(exif_data)

    if location_coordinates[0] is None:
        return None

    rounded_coordinates = round_coordinates(location_coordinates)

    if rounded_coordinates in _LOCATION_CACHE:
        return _LOCATION_CACHE[rounded_coordinates]

    location = rg.search(location_coordinates)[0]
    _LOCATION_CACHE[rounded_coordinates] = location

    return location


def get_exif_creation(exif_data: Dict) -> datetime:
    creation_time = None

    if 'EXIF DateTimeOriginal' in exif_data:
        creation_time = datetime.strptime(str(exif_data['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')

    return creation_time


def round_coordinates(location_coordinates: Coordinates) -> Coordinates:
    return tuple(round(c, 3) for c in location_coordinates)
