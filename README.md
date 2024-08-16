A python application that allows the user to view and edit the chunk data of region files in their minecraft world. This application is intended for the mca (Anvil) format

__**What needs to be done:**__
    - Short term
        - Allow multiple files to be parsed sequentially
            - This would require disk read/writes as opposed to memory read/writes due to minecraft worlds having potentially extremely large file sizes.
        - Make parsed NBT data easier to read
    - Long term
        - Implement GUI for ease