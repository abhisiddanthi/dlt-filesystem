#ifndef ENCODER_MSGPACK_TPP
#define ENCODER_MSGPACK_TPP

#include "encoderMsgPack.hpp"

namespace EncoderMsgPack {
    template <typename T>
    std::string Encoder::SerializeToHex(const T& data) {
        msgpack::sbuffer buffer;
        msgpack::pack(buffer, data);
        std::string encodedMessage = std::string(buffer.data(), buffer.size());
        std::string serializedToHex = "Z9dX7pQ3" + this->toHex(encodedMessage);
    
        return serializedToHex; 
    }
    
}

#endif 