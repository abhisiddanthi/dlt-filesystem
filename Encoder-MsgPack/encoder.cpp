#include <iostream>
#include <thread>
#include <string>
#include <iomanip>
#include <dlt/dlt.h>
#include <mutex>
#include <vector>
#include <chrono>
#include <cmath>
#include "encoderMsgPack.hpp"

// Declare a global DLT context
DLT_DECLARE_CONTEXT(ctx);

//Global Variables
std::mutex dataMutex;
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


//Thread to generate sinewave
void generateSineWave(const SineWave& wave, int sampleRate) {
    std::cout<<"working..\n";
    int t = 0; 
    while (running) {
        double value = wave.amplitude * sin(static_cast<double>(2 * M_PI * wave.frequency * (t / static_cast<double>(sampleRate)) + wave.phase));

        {
            std::lock_guard<std::mutex> lock(dataMutex);

            Signal sinewave = {wave.amplitude, wave.frequency, wave.phase, value};

            std::string serializedToHex = SerializeToHex(sinewave);

            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serializedToHex.c_str()));
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100)); 
        t++;
    }
}


int main()
{
    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING("App started"));

    //To send field data to encoder
    std::vector<std::string> fields = {"amplitude", "frequency", "phase", "value"};

    std::string fieldserializedToHex = SerializeToHex(fields);

    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(fieldserializedToHex.c_str()));

    SineWave wave = {1.0, 1.0, 0.0};
    int sampleRate = 100; 

    std::thread sineThread(generateSineWave, wave, sampleRate);

    std::this_thread::sleep_for(std::chrono::seconds(10));

    running = false;
    sineThread.join();

    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();

    std::cout << "finished" << "\n";

    return 0;
}
