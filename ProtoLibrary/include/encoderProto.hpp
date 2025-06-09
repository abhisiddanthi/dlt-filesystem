#ifndef ENCODER_PROTO_HPP
#define ENCODER_PROTO_HPP

#include <iostream>
#include <sstream>
#include <string>
#include <iomanip>
#include <memory>
#include <cstdio>      // For fprintf
#include <google/protobuf/message.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/reflection.h>
#include <google/protobuf/util/json_util.h> 
#include <tuple>
#include <utility>
#include <cstdint>
#include "../build/logger.pb.h"

namespace EncoderProto {
    class Encoder {
    private:
        std::string toHex(const std::string& input);

        // Available types to Encode
        void putValue (int32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (int64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (uint32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (uint64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (double value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (float value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (bool value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);
        void putValue (std::string value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m);

        template <typename Tuple, std::size_t... Is>
        void iterateTuple(const Tuple &t, std::shared_ptr<google::protobuf::Message> m, std::index_sequence<Is...>);

        template <typename Tuple>
        void iterateTuple(const Tuple &t, std::shared_ptr<google::protobuf::Message> m);

        template <typename T>
        void fillMessageContents(const T &obj, std::shared_ptr<google::protobuf::Message> m);

        std::shared_ptr<google::protobuf::Message> createMessageByType(const std::string& typeName);

    public:
        template <typename T>
        std::string SerializeToHex(const std::string& messageName, const T& data);
    };
}

#include "encoderProto.tpp"  

#endif 