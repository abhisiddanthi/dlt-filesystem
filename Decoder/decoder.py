import sine_wave_pb2 as sin_wave
import binascii
import json
from google.protobuf.json_format import MessageToDict

data = []

with open("logtest.dlt", "rb") as f:
    while True:
        header = f.read(12)  
        if not header or len(header) < 4:
            break

        header_type = header[0]
        header_length = 12 if header_type & 0x01 else 4

        if len(header) < header_length:
            print("Skipping incomplete header.")
            continue

        payload_length = (header[2] << 8) | header[3]

        payload = f.read(payload_length)
        if len(payload) < payload_length:
            print("Skipping incomplete payload.")
            continue

        decoded_payload = payload.decode('utf-8', errors='ignore')
        binary_data = binascii.unhexlify(decoded_payload)

        decoded_struct = sin_wave.SineWavePoint()
        decoded_struct.ParseFromString(binary_data)

        #print(decoded_struct)

        jsonObject = MessageToDict(decoded_struct)
        data.append(jsonObject)


with open("sinewaveout.json", "w") as file:
    json.dump(data, file, indent = 4)

        
