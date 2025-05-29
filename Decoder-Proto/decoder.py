import sine_wave_pb2 as sin_wave
import subprocess, csv, os
import binascii
import json
from google.protobuf.json_format import MessageToDict

data = []

dltpath = "../output.dlt"

result = subprocess.run(['dlt-viewer', '-s', '-csv', '-c', dltpath, 'parsed.csv'])

if result.returncode == 0:
    print("Converting to CSV Success")
    with open('parsed.csv', newline='') as file:
        reader = csv.reader(file, delimiter=' ', quotechar='|')

        for row in reader:
            # print(row)
            try:
                if row and row[-1].startswith("Z9dX7pQ3"):  
                    decoded_payload = row[-1][8:]
                    binary_data = binascii.unhexlify(decoded_payload)

                    try: 
                        decoded_struct = sin_wave.SineWavePoint()
                        decoded_struct.ParseFromString(binary_data)

                        jsonObject = MessageToDict(decoded_struct)
                        data.append([row[2], jsonObject])
                    
                    except Exception as e:
                        print(f"Skipping due to error: {e}")
                  
            except Exception as e:
                print(f"Incorrect data with pattern error: {e}")
                
    with open("sinewaveout.json", "w") as file:
        json.dump(data, file, indent = 4)

    if os.path.exists("parsed.csv"):
        os.remove("parsed.csv")
        print("Successfully removed temporary csv")
    else:
        print("File not found.")

else:
    print("Failed to Convert to csv")