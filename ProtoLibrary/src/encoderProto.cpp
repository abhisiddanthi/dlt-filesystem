#include "encoderProto.hpp"

namespace EncoderProto {

    //Type Support Functions:
    void Encoder::putValue (int32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetInt32(m.get(), field, value);
    }
    
    void Encoder::putValue (int64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetInt64(m.get(), field, value);
    }
    
    void Encoder::putValue (uint32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetUInt32(m.get(), field, value);
    }
    
    void Encoder::putValue (uint64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetUInt64(m.get(), field, value);
    }
    
    void Encoder::putValue (double value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetDouble(m.get(), field, value);
    }
    
    void Encoder::putValue (float value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetFloat(m.get(), field, value);
    }
    
    void Encoder::putValue (bool value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field,std::shared_ptr<google::protobuf::Message> m) {
        refl->SetBool(m.get(), field, value);
    }

    void Encoder::putValue (std::string value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
        refl->SetString(m.get(), field, value);
    }    

    std::string Encoder::toHex(const std::string& input) { 
        std::ostringstream hex_stream;
        for (unsigned char c : input) {
            hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
        }
        return hex_stream.str();
    }

    std::shared_ptr<google::protobuf::Message> Encoder::createMessageByType(const std::string& typeName) {
        std::string fullName = typeName;
        if (fullName.find('.') == std::string::npos) {
            fullName = "logger." + typeName;
        }
    
        const google::protobuf::Descriptor* descriptor =
            google::protobuf::DescriptorPool::generated_pool()->FindMessageTypeByName(fullName);
        if (!descriptor) {
            std::cerr << "Message type \"" << fullName << "\" not found." << std::endl;
            return nullptr;
        }
    
        const google::protobuf::Message* prototype =
            google::protobuf::MessageFactory::generated_factory()->GetPrototype(descriptor);
        if (!prototype) {
            std::cerr << "Prototype for message type \"" << fullName << "\" not available." << std::endl;
            return nullptr;
        }
    
        return std::shared_ptr<google::protobuf::Message>(prototype->New());
    }    

}