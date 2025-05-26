from pydlt import (
    ArgumentString,
    DltFileWriter,
    DltMessage,
    MessageLogInfo,
    MessageType,
    StorageHeader,
)

# Initialize the DLT Writer
with DltFileWriter("./DLTS/sinewave.dlt") as writer:
    with open("./sinewave_output.txt", "r") as file:
        for line in file:
            msg = DltMessage.create_verbose_message(
                [ArgumentString(line)],
                MessageType.DLT_TYPE_LOG,
                MessageLogInfo.DLT_LOG_INFO,
                "App",
                "Ctx",
                message_counter=0,
                str_header=StorageHeader(0, 0, "Ecu"),
            )
            writer.write_message(msg) 

print("DLT file 'logs.dlt' has been successfully created.")
