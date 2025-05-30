#include <iostream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <string>
#include <dlt/dlt.h>
#include <mutex>
#include <chrono>
#include <cmath>
#include "encoderProto.hpp"

using namespace std;

// Declare a global DLT context
DLT_DECLARE_CONTEXT(ctx);

//Global Variables
mutex dataMutex;
bool running = true;

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
};

//Thread to generate sinewave
void generateSineWave(const SineWave& wave, int sampleRate) {
    cout << " working..." << "\n ";
    int t = 0; 
    while (running) {
        double value = wave.amplitude * sin(2 * M_PI * wave.frequency * (t / static_cast<double>(sampleRate)) + wave.phase);

        {
            lock_guard<mutex> lock(dataMutex);

            Signal sinewave = {wave.amplitude, wave.frequency, wave.phase, value};

            string serializedToHex = SerializeToHex(sinewave);

            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serializedToHex.c_str()));
        }

        this_thread::sleep_for(chrono::milliseconds(100)); 
        t++;
    }
}


int main()
{   
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING("App started"));

    SineWave wave = {1.0, 1.0, 0.0};
    int sampleRate = 100; 

    thread sineThread(generateSineWave, wave, sampleRate);

    this_thread::sleep_for(chrono::seconds(30));

    running = false;
    sineThread.join();

    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();

    cout << "finished" << "\n";

    return 0;
}