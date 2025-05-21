#include <iostream>
#include <string>
#include "./build/logger.pb.h"
#include <fstream>
#include <nlohmann/json.hpp>
#include <dlt/dlt.h> //DLT Logging

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
    // To verify correct protobuf
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    // Register the DLT application and context
    DLT_REGISTER_APP("ENCD", "Encoder Application");
    DLT_REGISTER_CONTEXT(ctx, "ENC1", "Encoder Context");

    // Code to take input from JSON and put into Log Class
    ifstream f("../input.json"); // open input json file
    json data = json::parse(f);  // parse json into a list of objects

    // Temporary Output File
    // ofstream outputFile("../output.txt");
    // ofstream dltFile("../output.dlt"); // For simulated DLT logs

    // Code to encode the log object to string (Should be 1-2 lines max)
    for (auto element : data)
    {
        Log log = toProto(element);
        string encodedMessage;
        log.SerializeToString(&encodedMessage);


        //if (outputFile.is_open())
         //   outputFile << encodedMessage << endl;
        //else
          //  cerr << "Unable to open file" << endl;



        // Log the encoded message to DLT
        DLT_LOG(ctx, DLT_LOG_INFO, DLT_CSTRING("Encoded Protobuf Message:"), DLT_CSTRING(encodedMessage.c_str()));
    }

    // Unregister context and app
    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();

    // Write raw binary to .dlt file
    // dltFile.write(encodedMessage.data(), encodedMessage.size());
    // outputFile.close();
    // dltFile.close();

    // Code to log that one line onto a dlt file
    //(Couldn't find cpp library for that might have to use python for the POC)
    // Or can do a fake call to aralogger but still need to use some library for POC

    // Final dlt file should have all Json objects in the input.json file

    return 0;
}


//SET THE LD_LIBRARY_PATH 
//export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

//THEN RUN THE DLT-DAEMON
//dlt-receive -o encoder_logs.dlt localhost



