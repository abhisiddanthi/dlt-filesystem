#ifndef ENCODER_MSGPACK_HPP
#define ENCODER_MSGPACK_HPP

#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <msgpack.hpp>

namespace EncoderMsgPack {
    class Encoder {
    private:
        std::string toHex(const std::string& input);
    public:
        template <typename T>
        std::string SerializeToHex(const T& data);
    };
}

#include "encoderMsgPack.tpp"  

#endif 