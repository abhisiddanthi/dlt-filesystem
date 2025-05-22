import logger_pb2 as logger
import binascii
import json
from pydlt import DltFileReader
from google.protobuf.json_format import MessageToDict

data = []

for mesage in DltFileReader("./DLTS/testfile_extended.dlt"):
    message = "0801121308e20f1004181c2016282f301d38d8dacab7031a080801108ab2b0c106200230013805421053616d706c65207061796c6f61642031"
    binary_data = binascii.unhexlify(message)

    decoded = logger.Log()
    decoded.ParseFromString(binary_data)

    jsonObject = MessageToDict(decoded)
    data.append(jsonObject)

with open("output.json", "w") as file:
    json.dump(data, file, indent = 4)
