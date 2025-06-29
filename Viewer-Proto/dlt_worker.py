import os
import csv
import sys
import binascii
import importlib
from utils import APP_TEMP_DIR, run_command
from google.protobuf.json_format import MessageToDict
from google.protobuf import symbol_database
from PyQt6.QtCore import QThread, pyqtSignal

class DLTWorker(QThread):
    finished = pyqtSignal(str, dict)
    error = pyqtSignal(str)

    def __init__(self, dltpath, module_name):
        super().__init__()
        self.dltpath = dltpath
        self.module_name = module_name
        self.reported_missing_types = set()

    def createMessageByType(self, type_name: str):
        if '.' not in type_name:
            type_name = "logger." + type_name
        try:
            sym_db = symbol_database.Default()
            message_class = sym_db.GetSymbol(type_name)
            return message_class()
        except KeyError:
            if type_name not in self.reported_missing_types:
                self.reported_missing_types.add(type_name)
                display_name = type_name.replace("logger.", "")
                self.error.emit(f"Message type \"{display_name}\" not found. \n Please check whether if correct \".proto\" uploaded")
            return None
            
    def parse_dlt_line(self, line):
        if isinstance(line, list) and all(isinstance(item, str) for item in line):
            line = ' '.join(line)

        if isinstance(line, str):
            parts = line.split()
        else:
            return None

        if len(parts) >= 14:
            appid = parts[5]
            cntxid = parts[6]
            payload = ' '.join(parts[13:])
            return {
                'APPID': appid,
                'CNTXID': cntxid,
                'Payload': payload
            }

        return None

    def run(self):
        try:
            if APP_TEMP_DIR not in sys.path:
                sys.path.insert(0, APP_TEMP_DIR)
            importlib.import_module(self.module_name)
            struct_dict = {}

            csvname =  os.path.basename(self.dltpath)[:-4] + '.csv'
            csvpath = f'{APP_TEMP_DIR}/{csvname}'

            result = run_command(['dlt-viewer', '-v', '-s', '-csv', '-c', self.dltpath, csvpath])

            if result.returncode != 0:
                self.error.emit("Failed to convert to CSV")
                return

            with open(csvpath, newline='', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)

                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample)
                except csv.Error:
                    dialect = csv.get_dialect('excel')

                reader = csv.reader(file, dialect)
                for row in reader:
                    try:
                        payload = self.parse_dlt_line(row)['Payload']
                        appid = self.parse_dlt_line(row)['APPID']
                        cntxid = self.parse_dlt_line(row)['CNTXID']

                        if appid not in struct_dict:
                            struct_dict[appid] = {}

                        if cntxid not in struct_dict[appid]:
                            struct_dict[appid][cntxid] = {}

                        if row and payload.startswith("$%.&") and "&*.%" in payload:
                            remainder = payload[4:]
                            sep_index = remainder.find("&*.%")
                            messageName = remainder[:sep_index]
                            decoded_payload = remainder[sep_index + len("&*.%"):]
                                
                            if messageName not in struct_dict[appid][cntxid]:
                                struct_dict[appid][cntxid][messageName] = []

                            binary_data = binascii.unhexlify(decoded_payload)
                            decoded_struct = self.createMessageByType(messageName)

                            if decoded_struct is None:
                                continue

                            decoded_struct.ParseFromString(binary_data)
                            jsonObject = MessageToDict(decoded_struct, including_default_value_fields=True)

                            struct_dict[appid][cntxid][messageName].append({
                                "timestamp": row[2],
                                **jsonObject
                            })

                    except Exception as e:
                        print(f"[DLTWorker] Skipping row due to error: {e}")
                        continue

            if os.path.exists(csvpath):
                os.remove(csvpath)

            self.finished.emit(self.dltpath, struct_dict)

        except Exception as e:
            self.error.emit(str(e))