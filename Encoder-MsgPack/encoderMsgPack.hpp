#ifndef ENCODER_MSGPACK_HPP
#define ENCODER_MSGPACK_HPP

#include <iostream>
#include <string>
#include <sstream>
#include <msgpack.hpp>

using namespace std;

//Converting to hex
string toHex(string input) {
    string serializedToHex;
    ostringstream hex_stream;

    for (unsigned char c : input) {
        hex_stream << hex << setw(2) << setfill('0') << static_cast<int>(c);
    }

    return hex_stream.str();
}

//Serializing using MsgPack
template <typename T>
string SerializeToHex(const T& data) {
    msgpack::sbuffer buffer;
    msgpack::pack(buffer, data);
    string encodedMessage = string(buffer.data(), buffer.size());
    string serializedToHex = "Z9dX7pQ3" + toHex(encodedMessage);

    return serializedToHex; 
}

#endif 