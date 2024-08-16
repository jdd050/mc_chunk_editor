""" extract.py
    This file reads the raw, compressed NBT data from a minecraft anvil file (mca)
    The NBT data is decompressed using zlib (RFC1950)
    The raw NBT data is parsed using nbtlib
    The data is now stored as JSON
"""

from tkinter.filedialog import askopenfilenames
import zlib
import nbtlib
import io
import re

# Get the file path
files = askopenfilenames()
while not files:
    files = askopenfilenames()

# Read all region files
region_files = {}
for file in files:
    with open(file, 'rb') as f:
        # read the data
        data = f.read()
        f.close()
        # save it in a dict
        file_name = re.search("r\\.\\-?\d+\\.\\-?\d+\\.mca", f.name)
        region_files[file_name.group()] = data


for file, region_data in region_files.items():
    # Obtain chunk offsets and sector counts
    location_header = region_data[0:4096]
    location_table_data = {}
    chunk_offset_info_size = 4
    for i in range(0, len(location_header), chunk_offset_info_size):
        if i + chunk_offset_info_size < 4096:
            # get the chunk data in individual bytes
            chunk_data = [byte for byte in location_header[i:i+chunk_offset_info_size]]
            # calculate the offset for this chunk:
            # the offset is a 24-bit integer, made up of three bytes concatenated using bitwise OR within the 24 bits
            # For example: in a sample [BYTE_0, BYTE_1, BYTE_2, BYTE_3], BYTE_3 is the sector count so we ignore it
            # the top 8 bits are BYTE_0 (BYTE_0 << 16), the middle 8 are BYTE_1 (BYTE_1 << 8), and the bottom 8 are BYTE_2
            offset = (chunk_data[0] << 16) | (chunk_data[1] << 8) | chunk_data[2]
            # calculate the sector size, where 1 sector = 4096 bytes
            # ratio example (x is known, solve for y): 1 sector/4096 bytes = x sectors/y bytes
            sector_size = chunk_data[3] * 4096
            # save the calculations
            location_table_data[offset] = sector_size
        else:
            print("EOF")


    # decompress chunk data
    # chunk data is compressed using zlib RFC1950
    # zlib.decompress(chunk_data) -> results in raw chunk data
    for offset, sector_size in location_table_data.items():
        end_chunk_data = (offset * 4096) + sector_size
        compressed_chunk_data = region_data[(offset * 4096):end_chunk_data]
        
        # If the chunk data is too short, skip it
        if len(compressed_chunk_data) < 5:
            continue

        # Read the length (first 4 bytes) and compression type (5th byte)
        data_length = int.from_bytes(compressed_chunk_data[:4], byteorder='big')
        compression_type = compressed_chunk_data[4]

        if compression_type != 2:
            # If the compression type is not zlib (type 2), skip it
            print(f"Unsupported compression type: {compression_type}")
            continue

        # Decompress the data (skipping the first 5 bytes: length + compression type)
        compressed_chunk_data = compressed_chunk_data[5:]

        try:
            decompressed_chunk_data = zlib.decompress(compressed_chunk_data)
        except zlib.error as e:
            print(f"Decompression error: {e}")
        
        # Parse the now raw NBT data and convert it into a JSON format
        nbt_data = nbtlib.File.parse(io.BytesIO(decompressed_chunk_data)) # parse() expects an IO object, so make the bytes object an IO object
        json_data = nbt_data.snbt()
        with open(f"{file}_chunk_data.txt", "w") as f:
            f.write(f"{json_data}\n")
            f.close()
        
### TODO:
# interpret bytes in chunk data to convert to NBT
# test modifying said NBT, recompress, rewrite, and testing changes in game
