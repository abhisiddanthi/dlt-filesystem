<h1 align="center">DLT File System</h1>

## About ##

The DLT filesystem is a way to encode and log data into dlt files where the payload remains a decodable string. The decoder can decode this string to get back the original struct data in the original formats.\
This JSON viewer is a simple GUI-based tool that allows users to load a JSON file and plot its numerical data. It lets users select which fields to use as the X and Y axes and generates a graph based on the selected data.

## Code Explanation (Decoder) ##

- The file <a href="./Decoder/dltsim.py">```dltsim.py```</a> is used to emulate a *.dlt* file since encoding right now only gives us a *.txt* file. (<a href="./Decoder/sinewave_output.txt">```sinewave_output.txt```</a>)

- The file <a href="./Decoder/decoder.py">```decoder.py```</a> is used to decode the *.dlt* file that we obtain. (<a href="./Decoder/sinewave.dlt">```sinewave.dlt```</a>)
- The library <a href="https://pypi.org/project/pydlt/">pydlt</a> is used. 
- The decoder code takes a *.dlt* file as an input and the python proto library (after compilation using Protoc compiler) to decode the strings which are in binary ASCII format.<br>
This is the <a href="./Decoder/sine_wave_pb2.py">```X_pb2.py```</a> file (The linked file is for sin wave proto)
- The binary string is then converted into a proto object which can be used to put the struct data into any format we wish.\
Here we have put the proto data into a *.json* in <a href="./Decoder/sinewaveout.json>">```sinewaveout.json```</a> 

## Code Explanation (JSON Viewer) ##
- The code to run for this is <a href="./JsonViewer/jsonviewer.py">```jsonviewer.py```</a>
- The library <a href="https://pypi.org/project/PyQt6/">PyQt6</a> has been used to create the GUI
- The GUI is simple to use. Just run the python program and we can upload a json file with numerical data in a predefined format similar to <a href="./Decoder/sinewaveout.json">```sinwave.json```</a> can be plotted on the GUI.
- For plotting matplotlib has been integrated into the program as seen in the code

## Dlt-filesystem Requirements  ##
Creating a dlt pipeline for an custom dlt format

- We are using local version of libprotoc (3.6.1) 
- Make sure proto files are in the same depth as their parents
- Encoder builds the protobuf files on it's own and path specified in main.cpp (Don't change path)
- Make the build for encoder before using (creates a function called encoder)
- While using fstream with cmake need to mention file paths relative from the build folder

How to use the DLT Logger?
- SET THE LD_LIBRARY_PATH: export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
- THEN RUN THE DLT-DAEMON: dlt-receive -o encoder_logs.dlt localhost

## JsonViewer ##

```bash
# Clone this project
$ git clone https://github.com/abhisiddanthi/dlt-filesystem

# Access
$ cd jsonviewer

# Install dependencies
$ npm install matplotlib
$ pip install pyqt6

# Run the project
$ python3 jsonviewer.py

# The gui will start running in a new window
```


<a href="#top">Back to top</a>

