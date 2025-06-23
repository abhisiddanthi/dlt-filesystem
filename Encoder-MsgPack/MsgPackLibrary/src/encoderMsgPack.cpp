#include "encoderMsgPack.hpp"

namespace EncoderMsgPack {

    std::string Encoder::toHex(const std::string& input) { 
        std::ostringstream hex_stream;
        for (unsigned char c : input) {
            hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
        }
        return hex_stream.str();
    }
    
}