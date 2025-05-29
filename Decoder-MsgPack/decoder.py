import subprocess, csv, os
import binascii
import json
import msgpack

data = []

dltpath = "../output.dlt"

result = subprocess.run(['dlt-viewer', '-s', '-csv', '-c', dltpath, 'parsed.csv'])

if result.returncode == 0:
    print("success")
    with open('parsed.csv', newline='') as file:
        reader = csv.reader(file, delimiter=' ', quotechar='|')

        for row in reader:
            print(row)
            if row and row[-1].startswith("Z9dX7pQ3"):  
                decoded_payload = row[-1][8:]
                binary_data = binascii.unhexlify(decoded_payload)

                try: 
                    unpacked_data = msgpack.unpackb(binary_data, raw=False)
                    print(unpacked_data)
                    data.append(unpacked_data)
                
                except Exception as e:
                    print(f"Skipping due to error: {e}")
                
    with open("sinewaveout.json", "w") as file:
        json.dump(data, file, indent = 4)

    if os.path.exists("parsed.csv"):
        os.remove("parsed.csv")
        print("Successfully removed temporary csv")
    else:
        print("File not found.")

else:
    print("failure")