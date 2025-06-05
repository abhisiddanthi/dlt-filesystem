#ifndef ENCODER_TPP
#define ENCODER_TPP

#include "Encoder.hpp"
#include <sstream>
#include <iomanip>

using namespace std;

string toHex(const string& input) {
    ostringstream hexStream;
    for (unsigned char c : input) {
        hexStream << hex << setw(2) << setfill('0') << static_cast<int>(c);
    }
    return hexStream.str();
}


template <typename T>
SineWavePoint toProto(const T& sinewave) {
    SineWavePoint point;
    point.mutable_amplitude()->set_value(sinewave.amplitudeLOG);
    point.mutable_frequency()->set_value(sinewave.frequencyLOG);
    point.mutable_phase()->set_value(sinewave.phaseLOG);
    point.mutable_value()->set_value(sinewave.valueLOG);
    return point;
}

// Encode Function Using Protobuf Serialization
template <typename T>
string ProtoEncoder<T>::encode(const T& data) {
    SineWavePoint point = toProto(data);
    string encodedMessage;
    point.SerializeToString(&encodedMessage);
    return "Z9dX7pQ3" + toHex(encodedMessage);
}

#endif
