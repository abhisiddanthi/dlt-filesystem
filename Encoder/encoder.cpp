#include <iostream>
#include <string>
#include "./build/logger.pb.h"
#include <fstream>
#include <sstream>
#include <nlohmann/json.hpp>
#include <dlt/dlt.h>

using json = nlohmann::json;

using namespace std;

// Declare a global DLT context
DLT_DECLARE_CONTEXT(ctx);

Log toProto(json element)
{
    Log log;
    log.set_index(element["index"]);

    Time &time = *log.mutable_time();
    time.set_year(element["time"]["year"]);
    time.set_month(element["time"]["month"]);
    time.set_day(element["time"]["day"]);
    time.set_hours(element["time"]["hours"]);
    time.set_minutes(element["time"]["minutes"]);
    time.set_seconds(element["time"]["seconds"]);
    time.set_nanos(element["time"]["nanos"]);

    Timestamp &timestamp = *log.mutable_timestamp();
    timestamp.set_index(element["timestamp"]["index"]);
    timestamp.set_timestamp(element["timestamp"]["timestamp"]);

    log.set_ecuid(element["ecuid"]);
    log.set_apid(element["apid"]);
    log.set_ctid(element["ctid"]);
    log.set_type(element["type"]);
    log.set_payload(element["payload"]);

    return log;
}

int main()
{
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    // Register the DLT application and context
    DLT_REGISTER_APP("ENCD", "Encoder Application");
    DLT_REGISTER_CONTEXT(ctx, "ENC1", "Encoder Context");

    ifstream f("../input.json"); 
    json data = json::parse(f);  

    for (auto element : data)
    {
        Log log = toProto(element);
        string encodedMessage;
        log.SerializeToString(&encodedMessage);

        string serializedToHex = "start";
        ostringstream hex_stream;
        for (unsigned char c : encodedMessage) {
            hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
        }

        serializedToHex += hex_stream.str();

        cout<<serializedToHex<<"\n";

        // Log the encoded message to DLT
        DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serializedToHex.c_str()));
    }

    // Unregister context and app
    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();

    return 0;
}






