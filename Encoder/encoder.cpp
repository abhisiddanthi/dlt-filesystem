#include <iostream>
#include <string>
#include "./build/sine_wave.pb.h"
#include <fstream>
#include <sstream>
#include <nlohmann/json.hpp>

#define DLT_HEADER_SIZE 12

using json = nlohmann::json;

using namespace std;

void write_dlt_log(const string &filename, const string &message) {
    ofstream file(filename, ios::binary | ios::app);
    if (!file) {
        cerr << "Error opening file!" << endl;
        return;
    }

    unsigned char header[DLT_HEADER_SIZE] = {0};
    header[0] = 0x01;  
    header[1] = 0x02;  
    header[2] = (message.size() >> 8) & 0xFF;  
    header[3] = message.size() & 0xFF;  

    memcpy(header + 4, "ECU1", 4);

    memcpy(header + 8, "\x00\x00\x00\x10", 4);

    file.write(reinterpret_cast<char *>(header), DLT_HEADER_SIZE);
    file.write(message.c_str(), message.size());

    file.close();
    cout << "Log written: " << message << endl;
}

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

int main()
{
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    ifstream f("../sinewavein.json"); 
    json data = json::parse(f);  

    for (const auto &element : data["points"])
    {
        SineWavePoint log = toProto(element);
        string encodedMessage;
        log.SerializeToString(&encodedMessage);

        string serializedToHex;
        ostringstream hex_stream;
        for (unsigned char c : encodedMessage) {
            hex_stream << hex << setw(2) << setfill('0') << static_cast<int>(c);
        }

        serializedToHex += hex_stream.str();

        write_dlt_log("logtest.dlt", serializedToHex);

        cout<<serializedToHex<<"\n";
    }

    return 0;
}






