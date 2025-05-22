# dlt-filesystem
Creating a dlt pipeline for an custom dlt format

- We are using local version of libprotoc (3.6.1) 
- Make sure proto files are in the same depth as their parents
- Encoder builds the protobuf files on it's own and path specified in main.cpp (Don't change path)
- Make the build for encoder before using (creates a function called encoder)
- While using fstream with cmake need to mention file paths relative from the build folder

- How to use the DLT Logger?
- SET THE LD_LIBRARY_PATH: export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
- THEN RUN THE DLT-DAEMON: dlt-receive -o encoder_logs.dlt localhost
