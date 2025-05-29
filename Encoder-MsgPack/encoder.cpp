#include <iostream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <string>
#include <dlt/dlt.h>
#include <msgpack.hpp>
#include <mutex>
#include <chrono>
#include <cmath>

using namespace std;

// Declare a global DLT context
DLT_DECLARE_CONTEXT(ctx);

//Global Variables
mutex dataMutex;
bool running = true;

// Sinewave struct to encode
struct SineWave {
    double amplitude;
    double frequency;
    double phase;
};

struct Signal {
    double amplitudeLOG;
    double frequencyLOG;
    double phaseLOG;
    double valueLOG;

    MSGPACK_DEFINE(amplitudeLOG, frequencyLOG, phaseLOG, valueLOG)
};

//Converting to hex
string toHex(string input) {
    string serializedToHex;
    ostringstream hex_stream;

    for (unsigned char c : input) {
        hex_stream << hex << setw(2) << setfill('0') << static_cast<int>(c);
    }

    return hex_stream.str();
}

//Thread to generate sinewave
void generateSineWave(const SineWave& wave, int sampleRate) {
    int t = 0; 
    while (running) {
        double value = wave.amplitude * sin(2 * M_PI * wave.frequency * (t / static_cast<double>(sampleRate)) + wave.phase);

        {
            lock_guard<mutex> lock(dataMutex);

            Signal sinewave = {wave.amplitude, wave.frequency, wave.phase, value};

            msgpack::sbuffer buffer;
            msgpack::pack(buffer, sinewave);
            string encodedMessage = string(buffer.data(), buffer.size());
            string serializedToHex = "Z9dX7pQ3" + toHex(encodedMessage);

            cout<<serializedToHex<<"\n";

            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serializedToHex.c_str()));
        }

        cout << value << "\n";

        this_thread::sleep_for(chrono::milliseconds(100)); 
        t++;
    }
}


int main()
{
    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING("App started"));

    SineWave wave = {1.0, 1.0, 0.0};
    int sampleRate = 100; 

    thread sineThread(generateSineWave, wave, sampleRate);

    this_thread::sleep_for(chrono::seconds(10));

    running = false;

    this_thread::sleep_for(chrono::seconds(10));

    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();

    return 0;
}