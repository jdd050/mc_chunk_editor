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
import os
import sys

class ExtractData:
    # Ask for file paths upon class initialization
    def __init__(self):
        # Instance variables
        self.file_paths = askopenfilenames()
        self.script_loc = re.sub("/[a-zA-Z0-9]+\\.py", "", sys.argv[0])
        # Repeat until files are selected
        while not self.file_paths:
            self.file_paths = askopenfilenames()
        # Initialize temp dir
        if os.path.isdir(f"{self.script_loc}/temp"):
            for f in os.listdir(f"{self.script_loc}/temp"):
                os.remove(os.path.join(f"{self.script_loc}/temp", f))
        else:
            os.mkdir(f"{self.script_loc}/temp")
            

    def read_region_chunks(self) -> None:
        """
        Reads mca files raw data, then fetches the first 8 KiB that contain chunk offsets and sector size.
        The offset and sector size is then used to fetch the chunk data
            - Chunk data is stored in the filesystem due to size constraints
        """
        for file in self.file_paths:
            # Dict to temp store chunk file locations
            chunk_locations = {}
            # Read the raw data
            with open(file, 'rb') as f:
                raw_data = f.read()
                f.close()
                file_name = re.search("r\\.\\-?\d+\\.\\-?\d+\\.mca", f.name)
                offset_table = raw_data[0:4096]
                # Parse offset header, each entry is 4 bytes
                for i in range(0, len(offset_table), 4):
                    if i + 4 < 4096:
                        # Calculate the offset for this chunk:
                        # The offset is a 24-bit integer, made up of three bytes concatenated using bitwise OR within the 24 bits
                        # For example: in a sample [BYTE_0, BYTE_1, BYTE_2, BYTE_3], BYTE_3 is the sector count so we ignore it
                        # The top 8 bits are BYTE_0 (BYTE_0 << 16), the middle 8 are BYTE_1 (BYTE_1 << 8), and the bottom 8 are BYTE_2
                        info = [byte for byte in offset_table[i:i+4]]
                        offset = (info[0] << 16) | (info[1] << 8) | info[2]
                        # calculate the sector size, where 1 sector = 4096 bytes
                        # ratio example (x is known, solve for y): 1 sector/4096 bytes = x sectors/y bytes
                        sector_size = info[3] * 4096
                        chunk_locations[offset] = sector_size
                    else:
                        print("EOF")
                # Go to chunk data location, decompress the data, and store it in a temp directory
                for offset, sector_size in chunk_locations.items():
                    end_chunk_data = (offset * 4096) + sector_size
                    compressed_data = raw_data[(offset * 4096):end_chunk_data]
                    # If the chunk data is too short, skip it
                    if len(compressed_data) < 5:
                        continue
                    # Read the length (first 4 bytes) and the compression type (5th byte)
                    data_len = int.from_bytes(compressed_data[:4], byteorder='big')
                    compression_type = compressed_data[4]
                    if compression_type != 2:
                        print(f"Unsupported compression type: {compression_type}")
                        continue
                    # Now, decompress the data and store it
                    with open(f"{self.script_loc}/temp/{file_name.group()}_chunk{offset}.txt", "w") as f:  
                        try:
                            decompressed_data = zlib.decompress(compressed_data[5:])
                            nbt_data = nbtlib.File.parse(io.BytesIO(decompressed_data)) # parse() expects an IO object
                            json_data = nbt_data.unpack(json=True)
                            f.write(f"{json_data}")
                            f.close()
                        except zlib.error as e:
                            print(f"Decompression error: {e}")
                            f.close()
        return None

    def edit_foo(self) -> None:
        print("Not implemented")
        pass

instance = ExtractData()
instance.read_region_chunks()
instance.edit_foo()
