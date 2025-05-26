import sine_wave_pb2 as sin_wave
import binascii
import json
from pydlt import DltFileReader
from google.protobuf.json_format import MessageToDict

data = []

for message in DltFileReader("./DLTS/sinewave.dlt"):
    serializedHex = str(message.payload).rstrip()
    binary_data = binascii.unhexlify(serializedHex)

    decoded = sin_wave.SineWavePoint()
    decoded.ParseFromString(binary_data)

    print(decoded)

    jsonObject = MessageToDict(decoded)
    data.append(jsonObject)

with open("sinewaveout.json", "w") as file:
    json.dump(data, file, indent = 4)
