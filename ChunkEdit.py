""" ChunkEdit.py
    A python application that allows the user to view and edit the chunk data of region files in their minecraft world.
    This application is intended for the mca (Anvil) format
"""

from tkinter.filedialog import askopenfilenames
import zlib

# Get the file path
files = askopenfilenames()
while not files:
    files = askopenfilenames()

# Read the entire region file
for file in files:
    with open(file, 'rb') as f:
        region_data = f.read()
        f.close()

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
        with open("chunk_data.txt", "w") as f:
            f.write(f"{decompressed_chunk_data}\n")
            f.close()
    except zlib.error as e:
        print(f"Decompression error: {e}")
        
### TODO:
# interpret bytes in chunk data to convert to NBT
# test modifying said NBT, recompress, rewrite, and testing changes in game
