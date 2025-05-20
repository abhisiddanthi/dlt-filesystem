# dlt-filesystem
Creating a dlt pipeline for an custom dlt format

- We are using local version of libprotoc (3.6.1) 
- Make sure proto files are in the same depth as their parents
- Encoder builds the protobuf files on it's own and path specified in main.cpp (Don't change path)
- Make the build for encoder before using (creates a function called encoder)
