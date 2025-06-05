#ifndef ENCODER_TPP
#define ENCODER_TPP

#include "Encoder.hpp"

using namespace std;

// Helper function moved here instead of Encoder.hpp
string toHex(const string& input) {
    ostringstream hexStream;
    for (unsigned char c : input) {
        hexStream << hex << setw(2) << setfill('0') << static_cast<int>(c);
    }
    return hexStream.str();
}

template <typename T>
string MsgPackEncoder<T>::encode(const T& data) {
    msgpack::sbuffer buffer;
    msgpack::pack(buffer, data);
    string encodedMessage(buffer.data(), buffer.size());
    return "Z9dX7pQ3" + toHex(encodedMessage);
}

#endif
