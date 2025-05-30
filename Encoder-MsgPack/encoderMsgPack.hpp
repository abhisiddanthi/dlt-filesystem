#ifndef ENCODER_MSGPACK_HPP
#define ENCODER_MSGPACK_HPP

#include <iostream>
#include <string>
#include <sstream>
#include <msgpack.hpp>

//Converting to hex
std::string toHex(std::string input) {
    std::string serializedToHex;
    std::ostringstream hex_stream;

    for (unsigned char c : input) {
        hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
    }

    return hex_stream.str();
}

//Serializing using MsgPack
template <typename T>
std::string SerializeToHex(const T& data) {
    msgpack::sbuffer buffer;
    msgpack::pack(buffer, data);
    std::string encodedMessage = std::string(buffer.data(), buffer.size());
    std::string serializedToHex = "Z9dX7pQ3" + toHex(encodedMessage);

    return serializedToHex; 
}

#endif 