"""Background worker for processing DLT files."""
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
    """Worker thread for converting DLT files to structured data."""
    finished = pyqtSignal(str, dict)  # (dltpath, parsed_data)
    error = pyqtSignal(str)  # error_message

    def __init__(self, dlt_path, module_name):
        """
        Initialize DLT worker.
        
        Args:
            dlt_path: Path to DLT file
            module_name: Protobuf module name
        """
        super().__init__()
        self.dlt_path = dlt_path
        self.module_name = module_name
        self.reported_missing_types = set()

    def create_message_by_type(self, type_name: str):
        """Create protobuf message instance by type name.
        
        Args:
            type_name: Protobuf message type name
            
        Returns:
            Protobuf message instance or None
        """
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
                self.error.emit(
                    f"Message type \"{display_name}\" not found.\n"
                    "Please check if correct \".proto\" file is uploaded"
                )
            return None

    @staticmethod
    def parse_dlt_line(line):
        """Parse DLT log line into components.
        
        Args:
            line: Raw log line
            
        Returns:
            Parsed components dictionary or None
        """
        if isinstance(line, list) and all(isinstance(item, str) for item in line):
            line = ' '.join(line)

        if not isinstance(line, str):
            return None

        parts = line.split()
        if len(parts) < 14:
            return None

        app_id = parts[5]
        ctx_id = parts[6]
        payload = ' '.join(parts[13:])
        return {
            'APPID': app_id,
            'CNTXID': ctx_id,
            'Payload': payload
        }

    def run(self):
        """Main processing logic executed in worker thread."""
        try:
            # Ensure temp directory is in Python path
            if APP_TEMP_DIR not in sys.path:
                sys.path.insert(0, APP_TEMP_DIR)
            
            # Import protobuf module
            importlib.import_module(self.module_name)
            struct_dict = {}
            
            # Prepare CSV path
            csv_name = os.path.basename(self.dlt_path)[:-4] + '.csv'
            csv_path = f'{APP_TEMP_DIR}/{csv_name}'
            
            # Convert DLT to CSV
            result = run_command(['dlt-viewer', '-v', '-s', '-csv', '-c', self.dlt_path, csv_path])
            if result.returncode != 0:
                self.error.emit("Failed to convert DLT to CSV")
                return

            # Process CSV file
            with open(csv_path, newline='', encoding='utf-8') as file:
                # Detect CSV dialect
                sample = file.read(1024)
                file.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    dialect = csv.get_dialect('excel')
                
                reader = csv.reader(file, dialect)
                for row in reader:
                    try:
                        parsed = self.parse_dlt_line(row)
                        if not parsed:
                            continue
                            
                        payload = parsed['Payload']
                        app_id = parsed['APPID']
                        ctx_id = parsed['CNTXID']
                        
                        # Initialize data structure
                        if app_id not in struct_dict:
                            struct_dict[app_id] = {}
                        if ctx_id not in struct_dict[app_id]:
                            struct_dict[app_id][ctx_id] = {}
                        
                        # Process protobuf payload
                        if payload.startswith("$%.&") and "&*.%" in payload:
                            remainder = payload[4:]
                            sep_index = remainder.find("&*.%")
                            message_name = remainder[:sep_index]
                            decoded_payload = remainder[sep_index + len("&*.%"):]
                            
                            # Initialize message list
                            if message_name not in struct_dict[app_id][ctx_id]:
                                struct_dict[app_id][ctx_id][message_name] = []
                            
                            # Decode binary data
                            binary_data = binascii.unhexlify(decoded_payload)
                            decoded_struct = self.create_message_by_type(message_name)
                            if not decoded_struct:
                                continue
                            
                            # Parse protobuf and convert to dict
                            decoded_struct.ParseFromString(binary_data)
                            json_obj = MessageToDict(
                                decoded_struct, 
                                including_default_value_fields=True
                            )
                            
                            # Store parsed data
                            struct_dict[app_id][ctx_id][message_name].append({
                                "timestamp": row[2],
                                **json_obj
                            })
                    except Exception as e:
                        print(f"[DLTWorker] Skipping row: {e}")
                        continue

            # Clean up temporary file
            if os.path.exists(csv_path):
                os.remove(csv_path)

            self.finished.emit(self.dlt_path, struct_dict)

        except Exception as e:
            self.error.emit(f"DLT processing failed: {str(e)}")