<h1 align="center">DLT File System</h1>

## About ##

The DLT filesystem is a way to encode and log data into dlt files where the payload remains a decodable string. The decoder can decode this string to get back the original struct data in the original formats.\
This JSON viewer is a simple GUI-based tool that allows users to load a JSON file and plot its numerical data. It lets users select which fields to use as the X and Y axes and generates a graph based on the selected data.

## Code Explanation (Encoder) ##
The Encoder is responsible for serializing sine wave data and logging it into DLT (Diagnostic Log and Trace) for structured debugging and analysis. It calculates real-time sine wave values and converts them into a compact encoded format before logging them. Two versions of the encoder exist—one using MessagePack (MsgPack) and the other using Google Protocol Buffers (ProtoBuf).

###  Encoder-MsgPack  ###
- The file <a href="./Encoder-MsgPack/encoder.cpp">```encoder.cpp```</a> encodes sine wave data using MsgPack, a compact binary serialization format, and logs the output into DLT.
- The header file <a href="./Encoder-MsgPack/encoderMsgPack.hpp">```encoderMsgPack.hpp```</a> contains template functions, making serialization flexible for different data types.
- Key Functions in the Header:

   - toHex: Converts the serialized binary data into hexadecimal format for logging.

   - SerializeToHex<T> (Template Function):

      - Uses MsgPack to serialize any given data type (T), allowing dynamic struct encoding.

      - Packs the structured data into a binary MsgPack buffer, extracts it as a string, converts it to hex, and returns the serialized result.
- The encoder first logs structured field names (amplitude, frequency, phase, value) before processing sine wave data.
- The function <a href="./Encoder-MsgPack/encoder.cpp">```generateSineWave```</a> runs in a separate thread, dynamically computing sine wave values over time.
- Each computed sine wave value is stored in a Signal struct, then serialized using the SerializeToHex template function, converted to hex, and logged using DLT_LOG.


###  Encoder-Proto  ###
- The file <a href="./Encoder-Proto/encoder.cpp">```encoder.cpp```</a> encodes sine wave data using Google Protocol Buffers (ProtoBuf) and logs it into DLT.
- The header file <a href="./Encoder-Proto/encoderProto.hpp">```encoderProto.hpp```</a> contains template functions for structured serialization, including:

    - toHex: Converts binary data into hexadecimal format for logging.

    - toProto<T>: Converts a Signal struct into a SineWavePoint ProtoBuf object using mutator functions.

    - SerializeToHex<T>: Serializes the ProtoBuf object, converts it to hex, and returns the encoded output.
- The encoder first logs structured field names (amplitude, frequency, phase, value) before generating sine wave data.
- The function <a href="./Encoder-Proto/encoder.cpp">```generateSineWave```</a> runs in a separate thread, computing sine wave values dynamically.
- Each computed value is converted into a ProtoBuf object (SineWavePoint), serialized, transformed into hex, and logged using DLT_LOG.


## Code Explanation (Decoder) ##

- The file <a href="./Decoder/dltsim.py">```dltsim.py```</a> is used to emulate a *.dlt* file since encoding right now only gives us a *.txt* file. (<a href="./Decoder/sinewave_output.txt">```sinewave_output.txt```</a>)

- The file <a href="./Decoder/decoder.py">```decoder.py```</a> is used to decode the *.dlt* file that we obtain. (<a href="./Decoder/sinewave.dlt">```sinewave.dlt```</a>)
- The library <a href="https://pypi.org/project/pydlt/">pydlt</a> is used. 
- The decoder code takes a *.dlt* file as an input and the python proto library (after compilation using Protoc compiler) to decode the strings which are in binary ASCII format. This can be seen in the .txt file linked above.<br>
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
$ cd dlt-filesystem

# Install dependencies
$ npm install matplotlib
$ pip install pyqt6

# Run the project
$ python3 jsonviewer.py

# The gui will start running in a new window
```


<a href="#top">Back to top</a>

<!-- Notes for Author Use only -->
sudo nano /etc/dlt.conf

[General]
LogFilePath=/path/to/your/output.dlt
LogLevel=INFO

dlt-receive -a localhost -p 3490 -o output.dlt

ps aux | grep dlt-daemon

strip --remove-section=.note.ABI-tag libQt6Core.so.6

find / -name "libQt6Core.so.6" 2>/dev/null
