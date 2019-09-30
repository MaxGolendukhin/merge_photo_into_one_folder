import os
from PIL import Image
from datetime import datetime
import struct
import shutil


SOURCE_FOLDER = r'D:\Фото\Санья - 2019'
DESTINATION_FOLDER = r'D:\Фото\Санья - 2019\тест'


def get_date_taken(path):
    return Image.open(path)._getexif()[36867]


def get_mov_timestamps(filename):
    ''' Get the creation and modification date-time from .mov metadata.

        Returns None if a value is not available.
    '''

    ATOM_HEADER_SIZE = 8
    # difference between Unix epoch and QuickTime epoch, in seconds
    EPOCH_ADJUSTER = 2082844800

    creation_time = modification_time = None

    # search for moov item
    with open(filename, "rb") as f:
        while True:
            atom_header = f.read(ATOM_HEADER_SIZE)
            #~ print('atom header:', atom_header)  # debug purposes
            if atom_header[4:8] == b'moov':
                break  # found
            else:
                atom_size = struct.unpack('>I', atom_header[0:4])[0]
                f.seek(atom_size - 8, 1)

        # found 'moov', look for 'mvhd' and timestamps
        atom_header = f.read(ATOM_HEADER_SIZE)
        if atom_header[4:8] == b'cmov':
            raise RuntimeError('moov atom is compressed')
        elif atom_header[4:8] != b'mvhd':
            raise RuntimeError('expected to find "mvhd" header.')
        else:
            f.seek(4, 1)
            creation_time = struct.unpack('>I', f.read(4))[0] - EPOCH_ADJUSTER
            creation_time = datetime.fromtimestamp(creation_time)
            if creation_time.year < 1990:  # invalid or censored data
                creation_time = None

            modification_time = struct.unpack('>I', f.read(4))[0] - EPOCH_ADJUSTER
            modification_time = datetime.fromtimestamp(modification_time)
            if modification_time.year < 1990:  # invalid or censored data
                modification_time = None

    return creation_time, modification_time


def copy_file(origin_file_path, file, creation_time):
    destination_file_path = os.path.join(DESTINATION_FOLDER, creation_time + '_' + file)
    shutil.copy(origin_file_path, destination_file_path)


def create_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


create_folder(DESTINATION_FOLDER)

for root, dirs, files in os.walk(SOURCE_FOLDER, topdown=True):
    if DESTINATION_FOLDER == root:
        continue

    for file in files:
        file_path = os.path.join(root, file)

        if file_path.endswith('MOV'):
            creation_time, modification_time = get_mov_timestamps(file_path)
            creation_time = str(creation_time)
        elif file_path.endswith('JPG'):
            creation_time = get_date_taken(file_path)

        copy_file(file_path, file, creation_time.replace(':', '-'))
