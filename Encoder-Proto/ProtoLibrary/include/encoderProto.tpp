#ifndef ENCODER_PROTO_TPP
#define ENCODER_PROTO_TPP

#include "encoderProto.hpp"

namespace EncoderProto {
    template <typename Tuple, std::size_t... Is>
    void Encoder::iterateTuple(const Tuple &t, std::shared_ptr<google::protobuf::Message> m, std::index_sequence<Is...>) {
        const google::protobuf::Descriptor* desc = m->GetDescriptor();
        const google::protobuf::Reflection* refl = m->GetReflection();

        auto processIndex = [&](auto indexConstant) {
            constexpr std::size_t index = decltype(indexConstant)::value;
            auto value = std::get<index>(t);
            std::size_t myIndexVariable = index;
            const google::protobuf::FieldDescriptor* field = desc->field(myIndexVariable);

            this->putValue(value, refl, field, m);
        };

        using expander = int[];
        (void) expander {0, (processIndex(std::integral_constant<std::size_t, Is>{}), 0)...};
    }


    template <typename Tuple>
    void Encoder::iterateTuple(const Tuple &t, std::shared_ptr<google::protobuf::Message> m) {
        this->iterateTuple(t, m, std::make_index_sequence<std::tuple_size<Tuple>::value>{});
    }

    template <typename T>
    void Encoder::fillMessageContents(const T &obj, std::shared_ptr<google::protobuf::Message> m) {
        auto tup = obj.reflect();
        this->iterateTuple(tup, m);
    }

    template <typename T>
    std::string Encoder::SerializeToHex(const std::string& messageName, const T& data) {
        std::shared_ptr<google::protobuf::Message> m = this->createMessageByType(messageName);
        this->fillMessageContents(data, m);
        std::string encodedMessage;
        m->SerializeToString(&encodedMessage);
        std::string serializedToHex = "ZXd6" + messageName + "7pQ3" + this->toHex(encodedMessage);
        return serializedToHex;
    }

}

#endif 
