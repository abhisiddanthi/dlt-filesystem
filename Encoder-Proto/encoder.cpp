#include <iostream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <string>
#include <dlt/dlt.h>
#include <chrono>
#include <cmath>
#include "encoderProto.hpp"

#include <vector>
#include <tuple>

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
    Something testing;

    auto reflect() const {
        return std::tie(testing, value1, value2); 
    }
};

struct Signal {
    double amplitudeLOG;
    double frequencyLOG;
    double phaseLOG;
    double valueLOG;
    double othertestLOG;
    carexample thing;

    auto reflect() const {
        return std::tie(amplitudeLOG, frequencyLOG, phaseLOG, valueLOG, othertestLOG, thing); //Should be same as proto order
    }
};

struct PhoneNumber {
    std::string number;
    int32_t      type;
  
    // reflect() must return a std::tuple whose elements
    // line up 1:1 with the .proto fields
    auto reflect() const {
      return std::make_tuple(number, type);
    }
};

// Our mirror of tutorial::Person
struct Person {
    std::string              name;
    int32_t                  id;
    std::vector<std::string> emails;  // repeated string
    std::vector<PhoneNumber> phones;  // repeated PhoneNumber
    Signal sinewave;

    auto reflect() const {
        return std::make_tuple(name, id, emails, phones, sinewave);
    }
};

enum class Color
{
    RED = 0,
    GREEN = 1,
    BLUE = 2
};
 
struct Pixel
{
    Color c;
    std::vector<Color> palette;
    Person p;
    auto reflect() const { return std::tie(c, palette, p); }
};

//Thread to generate sinewave
void generateSineWave(const SineWave& wave, int sampleRate) {
    std::cout << " working..." << "\n ";
    int t = 0; 
    bool some = false;
    while (running) {
        double value = wave.amplitude * sin(2 * M_PI * wave.frequency * (t / static_cast<double>(sampleRate)) + wave.phase);
        // if(t<=2) some = true;

        {   
            Person p;
            p.name   = "Alice";
            p.id     = 42;
            p.emails = {"alice@example.com", "a.smith@work.org"};          
            PhoneNumber ph;
            ph.number = (t % 2 ? "555-1234" : "555-5678");
            ph.type   = (t % 2 ? 1 : 2);
            p.phones.push_back(ph);

                        
            Pixel pixel;
            pixel.c = Color::GREEN;
            pixel.palette = {Color::RED, Color::GREEN, Color::BLUE}; 
 

            Something testing = {"testingvalue"};
            carexample thing = {t, some, testing};

            Signal sinewave = {wave.amplitude, wave.frequency, wave.phase, value, t, thing};

            p.sinewave = sinewave;

            pixel.p = p;

            std::string serializedToHex = encoder.SerializeToHex("Pixel", pixel);
            
            int32_t v_int32 = 123;
            std::string hex_int32 = encoder.SerializeToHex(v_int32);
            std::cout << hex_int32 << std::endl;

            std::vector<int32_t> v_repeatedInt32 = {1, 2, 3};
            std::string hex_repeatedInt32 = encoder.SerializeToHex(v_repeatedInt32);
            std::cout << hex_repeatedInt32 << std::endl;

            int64_t v_int64 = 1234567890123;
            std::string hex_int64 = encoder.SerializeToHex(v_int64);
            std::cout << hex_int64 << std::endl;

            std::vector<int64_t> v_repeatedInt64 = {10000000000, 20000000000};
            std::string hex_repeatedInt64 = encoder.SerializeToHex(v_repeatedInt64);
            std::cout << hex_repeatedInt64 << std::endl;

            uint32_t v_uint32 = 4000000000;
            std::string hex_uint32 = encoder.SerializeToHex(v_uint32);
            std::cout << hex_uint32 << std::endl;

            std::vector<uint32_t> v_repeatedUInt32 = {100, 200, 300};
            std::string hex_repeatedUInt32 = encoder.SerializeToHex(v_repeatedUInt32);
            std::cout << hex_repeatedUInt32 << std::endl;

            uint64_t v_uint64 = 9000000000000000000ULL;
            std::string hex_uint64 = encoder.SerializeToHex(v_uint64);
            std::cout << hex_uint64 << std::endl;

            std::vector<uint64_t> v_repeatedUInt64 = {100000000000ULL, 200000000000ULL};
            std::string hex_repeatedUInt64 = encoder.SerializeToHex(v_repeatedUInt64);
            std::cout << hex_repeatedUInt64 << std::endl;

            float v_float = 3.14f;
            std::string hex_float = encoder.SerializeToHex(v_float);
            std::cout << hex_float << std::endl;

            std::vector<float> v_repeatedFloat = {1.1f, 2.2f, 3.3f};
            std::string hex_repeatedFloat = encoder.SerializeToHex(v_repeatedFloat);
            std::cout << hex_repeatedFloat << std::endl;

            double v_double = 6.283185307;
            std::string hex_double = encoder.SerializeToHex(v_double);
            std::cout << hex_double << std::endl;

            std::vector<double> v_repeatedDouble = {0.1, 0.01, 0.001};
            std::string hex_repeatedDouble = encoder.SerializeToHex(v_repeatedDouble);
            std::cout << hex_repeatedDouble << std::endl;

            bool v_bool = true;
            std::string hex_bool = encoder.SerializeToHex(v_bool);
            std::cout << hex_bool << std::endl;

            std::vector<bool> v_repeatedBool = {true, false, true};
            std::string hex_repeatedBool = encoder.SerializeToHex(v_repeatedBool);
            std::cout << hex_repeatedBool << std::endl;

            std::string v_string = "hello";
            std::string hex_string = encoder.SerializeToHex(v_string);
            std::cout << hex_string << std::endl;

            std::vector<std::string> v_repeatedString = {"foo", "bar"};
            std::string hex_repeatedString = encoder.SerializeToHex(v_repeatedString);
            std::cout << hex_repeatedString << std::endl;
            
            std::string rawBytes = "\xDE\xAD\xBE\xEF"; 
            std::string hexBytes = encoder.SerializeToHex(rawBytes);
            std::cout << "BytesMessage: " << hexBytes << "\n";

            std::vector<std::string> rawVec = {
                "\xDE\xAD\xBE\xEF",     // one blob
                "\xCA\xFE\xBA\xBE\x00"  // another blob
            };
            std::string hexVec = encoder.SerializeToHex(rawVec);
            std::cout << "RepeatedBytesMessage: " << hexVec << "\n";

            std::cout<< serializedToHex<<"\n";

            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hexVec.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hexBytes.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedString.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_string.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedBool.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_bool.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedDouble.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_double.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedFloat.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_float.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedUInt64.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_uint64.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedUInt32.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_uint32.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedInt64.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_int64.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_repeatedInt32.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hex_int32.c_str()));
            DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(serializedToHex.c_str()));
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100)); 
        // if(!some)t = t - 0.001;
        t++;
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