/**
 * @file encoderProto.cpp
 * @brief Defines non‐templated EncoderProto::Encoder member functions.
 *
 * Implements primitive and repeated‐field putValue overloads,
 * the toHex helper, and message‐factory createMessageByType().
 */

 #include "encoderProto.hpp"

 namespace EncoderProto {
 
     //==============================================================================
     /// @name Primitive single‐field overloads
     /// @{
     //==============================================================================
 
     /**
      * @brief Set an int32 field in a protobuf message.
      * @param value  The int32 value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(int32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetInt32(m.get(), field, value);
     }
 
     /**
      * @brief Set an int64 field in a protobuf message.
      * @param value  The int64 value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(int64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetInt64(m.get(), field, value);
     }
 
     /**
      * @brief Set a uint32 field in a protobuf message.
      * @param value  The uint32 value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(uint32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetUInt32(m.get(), field, value);
     }
 
     /**
      * @brief Set a uint64 field in a protobuf message.
      * @param value  The uint64 value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(uint64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetUInt64(m.get(), field, value);
     }
 
     /**
      * @brief Set a double field in a protobuf message.
      * @param value  The double value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(double value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetDouble(m.get(), field, value);
     }
 
     /**
      * @brief Set a float field in a protobuf message.
      * @param value  The float value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(float value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetFloat(m.get(), field, value);
     }
 
     /**
      * @brief Set a bool field in a protobuf message.
      * @param value  The bool value to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(bool value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetBool(m.get(), field, value);
     }
 
     /**
      * @brief Set a string field in a protobuf message.
      * @param value  The std::string to assign.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the target field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::string &value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         refl->SetString(m.get(), field, value);
     }
     //==============================================================================
     /// @}
     //==============================================================================
 
     //==============================================================================
     /// @name Repeated‐field overloads
     /// @{
     //==============================================================================
 
     /**
      * @brief Append multiple int32 values to a repeated field.
      * @param values Vector of int32 values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<int32_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddInt32(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple int64 values to a repeated field.
      * @param values Vector of int64 values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<int64_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddInt64(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple uint32 values to a repeated field.
      * @param values Vector of uint32 values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<uint32_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddUInt32(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple uint64 values to a repeated field.
      * @param values Vector of uint64 values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<uint64_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddUInt64(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple float values to a repeated field.
      * @param values Vector of float values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<float>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddFloat(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple double values to a repeated field.
      * @param values Vector of double values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<double>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddDouble(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple bool values to a repeated field.
      * @param values Vector of bool values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<bool>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (auto v : values) 
             refl->AddBool(m.get(), field, v);
     }
 
     /**
      * @brief Append multiple strings to a repeated field.
      * @param values Vector of std::string values.
      * @param refl   Reflection interface for the message.
      * @param field  Descriptor of the repeated field.
      * @param m      Shared pointer to the message instance.
      */
     void Encoder::putValue(const std::vector<std::string>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m) {
         for (const auto& v : values) 
             refl->AddString(m.get(), field, v);
     }
     //==============================================================================
     /// @}
     //==============================================================================
 
     //==============================================================================
     /// @name Helper Functions
     /// @{
     //==============================================================================
 
     /**
      * @brief Convert raw bytes into a lowercase hex string.
      * @param input Binary data to encode.
      * @return Hexadecimal representation.
      */
     std::string Encoder::toHex(const std::string& input) {
         std::ostringstream hex_stream;
         for (unsigned char c : input) {
             hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
         }
         return hex_stream.str();
     }
 
     /**
      * @brief Create a protobuf Message instance by its type name.
      * @param typeName Simple or fully qualified protobuf message name.
      * @return Shared pointer to a newly allocated Message, or nullptr on failure.
      */
     std::shared_ptr<google::protobuf::Message>
     Encoder::createMessageByType(const std::string& typeName) {
         std::string fullName = typeName;
         if (fullName.find('.') == std::string::npos) {
             fullName = "logger." + typeName;
         }
 
         const google::protobuf::Descriptor* descriptor =
             google::protobuf::DescriptorPool::generated_pool()
                 ->FindMessageTypeByName(fullName);
         if (!descriptor) {
             std::cerr << "Message type \"" << fullName << "\" not found." << std::endl;
             return nullptr;
         }
 
         const google::protobuf::Message* prototype =
             google::protobuf::MessageFactory::generated_factory()
                 ->GetPrototype(descriptor);
         if (!prototype) {
             std::cerr << "Prototype for message type \"" << fullName << "\" not available." << std::endl;
             return nullptr;
         }
 
         return std::shared_ptr<google::protobuf::Message>(prototype->New());
     }
     //==============================================================================
     /// @}
     //==============================================================================
 
 } // namespace EncoderProto
 