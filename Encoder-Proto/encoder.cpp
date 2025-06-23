#include <iostream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <string>
#include <dlt/dlt.h>
#include <chrono>
#include <cmath>
#include "encoderProto.hpp"

// Declare a global DLT context
DLT_DECLARE_CONTEXT(ctx);
EncoderProto::Encoder encoder;

//Global Variables
bool running = true;

struct SineWave {
    double amplitude;
    double frequency;
    double phase;
};

struct Something {
    std::string name; 

    auto reflect() const {
        return std::tie(name); 
    }
};

struct carexample {
    double value1;
    bool value2;

    auto reflect() const {
        return std::tie(value1, value2); 
    }
};

struct Signal {
    double amplitudeLOG;
    double frequencyLOG;
    double phaseLOG;
    double valueLOG;
    double othertestLOG;

    auto reflect() const {
        return std::tie(amplitudeLOG, frequencyLOG, phaseLOG, valueLOG, othertestLOG); //Should be same as proto order
    }
};

//Thread to generate sinewave
void generateSineWave(const SineWave& wave, int sampleRate) {
    std::cout << " working..." << "\n ";
    double t = 10; 
    bool some = false;
    while (running) {
        double value = wave.amplitude * sin(2 * M_PI * wave.frequency * (t / static_cast<double>(sampleRate)) + wave.phase);
        if(t<=2) some = true;

        {
            carexample thing = {t, some};

            // Signal sinewave = {wave.amplitude, wave.frequency, wave.phase, value, t+1};

            std::string serializedToHex = encoder.SerializeToHex("carthing", thing);

            std::cout<< value << serializedToHex<<"\n";

            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serializedToHex.c_str()));
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100)); 
        if(!some)t = t - 0.1;
    }
}

int main()
{   
    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING("App started"));

    // Something yes = {"testing value ofc"};
    // std::string serialized = encoder.SerializeToHex("Something", yes);

    // DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serialized.c_str()));

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