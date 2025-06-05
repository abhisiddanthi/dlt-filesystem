#include <iostream>
#include <thread>
#include <mutex>
#include <cmath>
#include <google/protobuf/stubs/common.h>
#include <Encoder.hpp>
#include <Logger.hpp>

using namespace std;

struct SineWave {
    double amplitude;
    double frequency;
    double phase;

    double generate(int t, int sampleRate) const {
        return amplitude * sin(2 * M_PI * frequency * (t / static_cast<double>(sampleRate)) + phase);
    }
};

struct Signal {
    double amplitudeLOG;
    double frequencyLOG;
    double phaseLOG;
    double valueLOG;
};

// **SineWaveGenerator class handles wave generation and logging**
class SineWaveGenerator {
private:
    mutex dataMutex;
    bool running;
    ProtoEncoder<Signal>* encoder;
    DLTLogger* logger;
    SineWave wave;
    int sampleRate;

public:
    SineWaveGenerator(ProtoEncoder<Signal>* enc, DLTLogger* log, double amp, double freq, double ph, int rate)
        : encoder(enc), logger(log), wave{amp, freq, ph}, sampleRate(rate), running(true) {}

    void generate() {
        int t = 0;
        while (running) {
            double value = wave.generate(t, sampleRate);

            {
                lock_guard<mutex> lock(dataMutex);
                Signal sinewave{wave.amplitude, wave.frequency, wave.phase, value};

                string encodedHex = encoder->encode(sinewave);
                logger->logData(encodedHex);
            }

            this_thread::sleep_for(chrono::milliseconds(100));
            t++;
        }
    }

    void start() {
        running = true;
        thread sineThread(&SineWaveGenerator::generate, this);
        this_thread::sleep_for(chrono::seconds(30));  
        stop();
        sineThread.join();
    }

    void stop() {
        running = false;
    }
};

int main() {
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    ProtoEncoder<Signal>* encoder = new ProtoEncoder<Signal>();
    DLTLogger* logger = new DLTLogger();
    logger->init();

    // **Start sine wave generation**
    SineWaveGenerator sineWave(encoder, logger, 1.0, 1.0, 0.0, 100);
    sineWave.start();

    logger->shutdown();
    delete encoder;
    delete logger;

    cout << "Finished" << "\n";
    return 0;
}
