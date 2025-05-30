#ifndef ENCODER_PROTO_HPP
#define ENCODER_PROTO_HPP

#include <iostream>
#include <string>
#include <sstream>
#include "./build/sine_wave.pb.h"

//Converting to hex
std::string toHex(std::string input) {
    std::string serializedToHex;
    std::ostringstream hex_stream;

    for (unsigned char c : input) {
        hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
    }

    return hex_stream.str();
}

// Convert to a SineWavePoint protobuf message
template <typename T>
SineWavePoint toProto(const T& sinewave)
{
    SineWavePoint point;
    point.mutable_amplitude()->set_value(sinewave.amplitudeLOG);
    point.mutable_frequency()->set_value(sinewave.frequencyLOG);    
    point.mutable_phase()->set_value(sinewave.phaseLOG);
    point.mutable_value()->set_value(sinewave.valueLOG);
    return point;
}

//Serializing using MsgPack
template <typename T>
std::string SerializeToHex(const T& data) {

    SineWavePoint point = toProto(data);
    std::string encodedMessage;
    point.SerializeToString(&encodedMessage);
    std::string serializedToHex = "Z9dX7pQ3" + toHex(encodedMessage);

    return serializedToHex; 
}

#endif 