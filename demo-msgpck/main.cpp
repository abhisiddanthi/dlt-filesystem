#include <iostream>
#include <thread>
#include <mutex>
#include <cmath>
#include <vector>
#include <chrono>
#include <Encoder.hpp>
#include <Logger.hpp>

using namespace std;

// Global Variables
mutex dataMutex;
bool running = true;

// SineWave struct for encoding
struct SineWave {
    double amplitude;
    double frequency;
    double phase;

    double generate(int t, int sampleRate) const {
        return amplitude * sin(2 * M_PI * frequency * (t / static_cast<double>(sampleRate)) + phase);
    }
};

// Signal struct with MsgPack serialization
struct Signal {
    double amplitudeLOG;
    double frequencyLOG;
    double phaseLOG;
    double valueLOG;

    MSGPACK_DEFINE(amplitudeLOG, frequencyLOG, phaseLOG, valueLOG);
};

// **SineWaveGenerator class handles wave generation and logging**
class SineWaveGenerator {
private:
    mutex dataMutex;
    bool running;
    MsgPackEncoder<Signal>* encoder;
    Logger* logger;
    SineWave wave;
    int sampleRate;

public:
    SineWaveGenerator(MsgPackEncoder<Signal>* enc, Logger* log, double amp, double freq, double ph, int rate)
        : encoder(enc), logger(log), wave{amp, freq, ph}, sampleRate(rate), running(true) {}

    void generate() {
        int t = 0;
        while (running) {
            double value = wave.generate(t, sampleRate);

            {
                lock_guard<mutex> lock(dataMutex);
                Signal sinewave{wave.amplitude, wave.frequency, wave.phase, value};

                string encodedHex = encoder->encode(sinewave);
                logger->logData(encodedHex);  // Logging encoded signal data
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
    Logger* logger = new Logger();
    logger->init();

    MsgPackEncoder<Signal>* signalEncoder = new MsgPackEncoder<Signal>();
    MsgPackEncoder<vector<string>>* fieldEncoder = new MsgPackEncoder<vector<string>>();

    // Encoding and logging field metadata
    vector<string> fields = {"amplitude", "frequency", "phase", "value"};
    string fieldSerializedHex = fieldEncoder->encode(fields);
    logger->logData(fieldSerializedHex);  // Log encoded field metadata

    // Start sine wave generation
    SineWaveGenerator sineWave(signalEncoder, logger, 1.0, 1.0, 0.0, 100);
    sineWave.start();

    // Cleanup
    logger->shutdown();
    delete signalEncoder;
    delete fieldEncoder;
    delete logger;

    cout << "Finished\n";
    return 0;
}
