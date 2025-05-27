#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <string>
#include <nlohmann/json.hpp>
#include <dlt/dlt.h>
#include "./build/sine_wave.pb.h"

using json = nlohmann::json;
using namespace std;

// Declare a global DLT context
DLT_DECLARE_CONTEXT(ctx);

// Convert a JSON element to a SineWavePoint protobuf message
SineWavePoint toProto(const json &element)
{
    SineWavePoint point;
    point.set_time(element["time"]);
    point.set_amplitude(element["amplitude"]);
    point.set_frequency(element["frequency"]);
    point.set_phase(element["phase"]);
    point.set_value(element["value"]);
    return point;
}

// Convert binary string to hex string
string toHex(const string &input)
{
    ostringstream oss;
    for (unsigned char c : input)
    {
        oss << hex << setw(2) << setfill('0') << static_cast<int>(c);
    }
    return oss.str();
}

int main()
{
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING("App started"));


    ifstream f("../sinewavein.json");
    if (!f.is_open())
    {
        cerr << "Failed to open json" << endl;
        return 1;
    }

    json data = json::parse(f);

    for (const auto &element : data["points"])
    {
        SineWavePoint point = toProto(element);

        string encodedMessage;
        point.SerializeToString(&encodedMessage);

        string hexString = "Z9dX7pQ3" + toHex(encodedMessage);


        cout << hexString << endl;

        // Log the encoded message to DLT
        DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hexString.c_str()));
    }

    this_thread::sleep_for(chrono::seconds(2));

    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();

    return 0;
}