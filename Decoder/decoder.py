import logger_pb2 as logger
import binascii
import json
from pydlt import DltFileReader
from google.protobuf.json_format import MessageToDict

data = []

for message in DltFileReader("./DLTS/simlogs.dlt"):
    serializedHex = str(message.payload).rstrip()
    binary_data = binascii.unhexlify(serializedHex)

    decoded = logger.Log()
    decoded.ParseFromString(binary_data)

    jsonObject = MessageToDict(decoded)
    data.append(jsonObject)

with open("output.json", "w") as file:
    json.dump(data, file, indent = 4)
