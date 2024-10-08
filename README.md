﻿# Minecraft Chunk Editor

A python application that allows the user to view and edit the chunk data of region files in their minecraft world. This application is intended for the mca (Anvil) format

## Developer notes
> 16 Aug 2024
- Chunk data extraction and parsing has been moved to *extract.py*
- *ChunkEdit.py* will be used for editing chunk data, hence the name. I also plan to possibly integrate the GUI here.
> 17 Aug 2024
- Cleaned up extract.py code and implemented memory optimization measures
- Working on json formatting for chunk data
  - Finished ✅ 
- 
## **What needs to be done:**
- Short term
  - ~~Allow multiple files to be parsed sequentially~~
    - ~~This would require disk read/writes as opposed to memory read/writes due to minecraft worlds having potentially extremely large file sizes.~~
  - Make parsed NBT data easier to read
- Long term
  - Implement GUI for ease
