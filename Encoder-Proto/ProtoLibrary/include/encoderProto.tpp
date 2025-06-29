/**
 * @file encoderProto.tpp
 * @brief Templated implementations for EncoderProto::Encoder methods.
 *
 * This file contains the definitions of all inline and template
 * functions declared in encoderProto.hpp, including reflection
 * iteration, field population, byte‐string detection, and
 * SerializeToHex overloads.
 */

 #ifndef ENCODER_PROTO_TPP
 #define ENCODER_PROTO_TPP
 
 #include "encoderProto.hpp"
 
 #include <unordered_map>
 #include <typeinfo>
 #include <string>
 #include <vector>
 #include <stdexcept>
 #include <algorithm>
 #include <cctype>
 
 //------------------------------------------------------------------------------
 //  global type → proto‐name map
 //------------------------------------------------------------------------------
 /**
  * @brief Returns a singleton map from C++ type_info to proto message names.
  *
  * Used by the data‐only SerializeToHex() overload to look up the
  * protobuf message type corresponding to a given C++ type.
  */
 static const std::unordered_map<const std::type_info*, std::string>& typeNameMap() {
     static const std::unordered_map<const std::type_info*, std::string> m = {
         { &typeid(int32_t),                           "NumberInt32"           },
         { &typeid(std::vector<int32_t>),              "RepeatedNumberInt32"   },
         { &typeid(int64_t),                           "NumberInt64"           },
         { &typeid(std::vector<int64_t>),              "RepeatedNumberInt64"   },
         { &typeid(uint32_t),                          "NumberUInt32"          },
         { &typeid(std::vector<uint32_t>),             "RepeatedNumberUInt32"  },
         { &typeid(uint64_t),                          "NumberUInt64"          },
         { &typeid(std::vector<uint64_t>),             "RepeatedNumberUInt64"  },
         { &typeid(float),                             "NumberFloat"           },
         { &typeid(std::vector<float>),                "RepeatedNumberFloat"   },
         { &typeid(double),                            "NumberDouble"          },
         { &typeid(std::vector<double>),               "RepeatedNumberDouble"  },
         { &typeid(bool),                              "NumberBool"            },
         { &typeid(std::vector<bool>),                 "RepeatedNumberBool"    },
         { &typeid(std::string),                       "NumberString"          },
         { &typeid(std::vector<std::string>),          "RepeatedNumberString"  }
     };
     return m;
 }
 
 //------------------------------------------------------------------------------
 //  Delimiters for framing serialized packets
 //------------------------------------------------------------------------------
 /** @brief Leading delimiter for each serialized packet. */
 static const std::string START_DELIM = "$%..&";
 /** @brief Trailing delimiter for each serialized packet. */
 static const std::string END_DELIM   = "&*.%";
 
 namespace EncoderProto {
 
 //---------------- iterateTuple & fillMessageContents ----------------
 
 /**
  * @brief Iterate over a reflect() tuple and populate a protobuf message.
  * @tparam Tuple    Type of the std::tuple returned by reflect().
  * @tparam Is       Index sequence for tuple unpacking.
  * @param t         The tuple of object fields.
  * @param m         Shared pointer to the protobuf message to fill.
  * @param            Index sequence to expand the tuple.
  */
 template <typename Tuple, std::size_t... Is>
 void Encoder::iterateTuple(const Tuple& t, std::shared_ptr<google::protobuf::Message> m, std::index_sequence<Is...>)
 {
     const auto* desc = m->GetDescriptor();
     const auto* refl = m->GetReflection();
     auto process = [&](auto idx) {
         constexpr std::size_t i = decltype(idx)::value;
         auto val = std::get<i>(t);
         auto* field = desc->field(i);
         putValue(val, refl, field, m);
     };
     (void)std::initializer_list<int>{
         (process(std::integral_constant<std::size_t,Is>{}), 0)...
     };
 }
 
 /**
  * @brief Helper that deduces tuple size and forwards to the indexed version.
  * @tparam Tuple Type of the reflect() tuple.
  * @param t      The tuple of object fields.
  * @param m      Shared pointer to the protobuf message to fill.
  */
 template <typename Tuple>
 void Encoder::iterateTuple(const Tuple& t, std::shared_ptr<google::protobuf::Message> m)
 {
     iterateTuple(t, m, std::make_index_sequence<std::tuple_size<Tuple>::value>{});
 }
 
 /**
  * @brief Populates all fields of a nested message from a user object.
  * @tparam T    Reflectable user type with .reflect().
  * @param obj   The object to serialize.
  * @param m     Shared pointer to the protobuf message.
  */
 template <typename T>
 void Encoder::fillMessageContents(const T& obj, std::shared_ptr<google::protobuf::Message> m)
 {
     auto tup = obj.reflect();
     iterateTuple(tup, m);
 }
 
 //----------------------- putValue (non‐enum) -----------------------
 
 /**
  * @brief Serialize a nested message field for non‐enum types.
  * @tparam T    Nested reflectable type.
  * @param obj   The nested object.
  * @param refl  Reflection interface of parent message.
  * @param field Descriptor of the message field.
  * @param m     Shared pointer to parent message.
  */
 template <typename T>
 typename std::enable_if<!std::is_enum<T>::value, void>::type
 Encoder::putValue(const T& obj, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m)
 {
     if (field->cpp_type() == google::protobuf::FieldDescriptor::CPPTYPE_MESSAGE) {
         auto* sub = refl->MutableMessage(m.get(), field);
         auto subPtr = std::shared_ptr<google::protobuf::Message>(
             sub, [](auto*){}
         );
         fillMessageContents(obj, subPtr);
     }
 }
 
 /**
  * @brief Serialize a repeated nested message field for non‐enum types.
  * @tparam T      Element type with .reflect().
  * @param values  Vector of nested objects.
  * @param refl    Reflection interface of parent message.
  * @param field   Descriptor of the repeated message field.
  * @param m       Shared pointer to parent message.
  */
 template <typename T>
 typename std::enable_if<!std::is_enum<T>::value, void>::type
 Encoder::putValue(const std::vector<T>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m)
 {
     if (field->is_repeated() &&
         field->cpp_type() == google::protobuf::FieldDescriptor::CPPTYPE_MESSAGE)
     {
         for (auto const& v : values) {
             auto* sub = refl->AddMessage(m.get(), field);
             auto subPtr = std::shared_ptr<google::protobuf::Message>(
                 sub, [](auto*){}
             );
             fillMessageContents(v, subPtr);
         }
     }
 }
 
 //------------------------ putValue (enum) ------------------------
 
 /**
  * @brief Serialize a C++ enum into a protobuf enum field.
  * @tparam E    Enum type.
  * @param value The enum value.
  * @param refl  Reflection interface of the message.
  * @param field Descriptor of the enum field.
  * @param m     Shared pointer to the message.
  */
 template <typename E>
 typename std::enable_if<std::is_enum<E>::value, void>::type
 Encoder::putValue(E value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m)
 {
     if (field->cpp_type() == google::protobuf::FieldDescriptor::CPPTYPE_ENUM) {
         refl->SetEnumValue(m.get(), field, static_cast<int>(value));
     }
 }
 
 /**
  * @brief Serialize a repeated C++ enum into a repeated protobuf enum.
  * @tparam E        Enum type.
  * @param values    Vector of enum values.
  * @param refl      Reflection interface of the message.
  * @param field     Descriptor of the repeated enum field.
  * @param m         Shared pointer to the message.
  */
 template <typename E>
 typename std::enable_if<std::is_enum<E>::value, void>::type
 Encoder::putValue(const std::vector<E>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m)
 {
     if (field->is_repeated() &&
         field->cpp_type() == google::protobuf::FieldDescriptor::CPPTYPE_ENUM)
     {
         for (auto v : values) {
             refl->AddEnumValue(m.get(), field, static_cast<int>(v));
         }
     }
 }
 
 //---------------------- byte‐string detectors ----------------------
 
 /**
  * @brief Catch‐all: non‐string types are never raw byte‐strings.
  * @tparam U Any type.
  * @return Always false.
  */
 template <typename U>
 bool Encoder::isByteString(const U&)
 {
     return false;
 }
 
 /**
  * @brief Detect if a std::string contains raw (non-printable) bytes.
  * @param s The string to inspect.
  * @return True if any character is non-printable.
  */
 bool Encoder::isByteString(const std::string& s)
 {
     return std::any_of(
         s.begin(), s.end(),
         [](unsigned char c){
             return (c < 32 && !std::isspace(c)) || c > 126;
         }
     );
 }
 
 /**
  * @brief Catch‐all: non‐vector<string> types are not repeated byte‐strings.
  * @tparam U Any type.
  * @return Always false.
  */
 template <typename U>
 bool Encoder::isRepeatedByteString(const U&)
 {
     return false;
 }
 
 /**
  * @brief Detect if any element of vector<string> is a raw byte‐string.
  * @param v The vector to inspect.
  * @return True if any element contains non-printable bytes.
  */
 bool Encoder::isRepeatedByteString(const std::vector<std::string>& v)
 {
     for (auto const& str : v) {
         if (Encoder::isByteString(str)) return true;
     }
     return false;
 }
 
 //---------------------- SerializeToHex (messageName + data) ----------------------
 
 /**
  * @brief Serialize data into a named protobuf message and hex‐encode it.
  * @tparam T            Type of data to serialize.
  * @param messageName   Protobuf message type name.
  * @param data          The object or value to encode.
  * @return Framed and hex‐encoded string.
  * @throws std::invalid_argument on error.
  */
 template <typename T>
 std::string Encoder::SerializeToHex(const std::string& messageName, const T& data)
 {
     try {
         auto m = createMessageByType(messageName);
         if (!m)
             throw std::runtime_error(
                 "SerializeToHex: could not create message for '" + messageName + "'"
             );
 
         fillMessageContents(data, m);
 
         std::string bin;
         if (!m->SerializeToString(&bin))
             throw std::runtime_error(
                 "SerializeToHex: protobuf serialization failed for '" + messageName + "'"
             );
 
         return START_DELIM + messageName + END_DELIM + toHex(bin);
     }
     catch (const std::invalid_argument&) {
         throw;
     }
     catch (const std::exception& ex) {
         throw std::invalid_argument(
             std::string("SerializeToHex failed for message '")
             + messageName + "': " + ex.what()
         );
     }
 }
 
 //---------------------- SerializeToHex (data only) ----------------------
 
 /**
  * @brief Serialize data based on its C++ type mapping and hex‐encode.
  * @tparam T Type of the data.
  * @param data The object or value to encode.
  * @return Framed and hex‐encoded string.
  * @throws std::invalid_argument on unknown type or error.
  */
 template <typename T>
 std::string Encoder::SerializeToHex(const T& data)
 {
     try {
         auto it = typeNameMap().find(&typeid(T));
         if (it == typeNameMap().end()) {
             throw std::runtime_error(
                 "SerializeToHex: unknown type '" + std::string(typeid(T).name()) + "'"
             );
         }
         const std::string& protoName = it->second;
 
         int byteChecker;
 
         std::shared_ptr<google::protobuf::Message> msg;
         if (isByteString(data)) {
             byteChecker = 1;
             msg = createMessageByType("NumberBytes");
             if (!msg)
                 throw std::runtime_error("SerializeToHex: could not create 'NumberBytes'");
         }
         else if (isRepeatedByteString(data)) {
             byteChecker = 2;
             msg = createMessageByType("RepeatedNumberBytes");
             if (!msg)
                 throw std::runtime_error("SerializeToHex: could not create 'RepeatedNumberBytes'");
         }
         else {
             msg = createMessageByType(protoName);
             if (!msg)
                 throw std::runtime_error("SerializeToHex: could not create '" + protoName + "'");
         }
 
         const auto* refl = msg->GetReflection();
         const auto* desc = msg->GetDescriptor();
         if (desc->field_count() != 1)
             throw std::runtime_error(
                 "SerializeToHex: message '" + protoName + "' must have exactly one field"
             );
         const auto* field = desc->field(0);
 
         putValue(data, refl, field, msg);
 
         std::string bin;
         if (!msg->SerializeToString(&bin))
             throw std::runtime_error(
                 "SerializeToHex: protobuf serialization failed for '" + protoName + "'"
             );
 
         if (byteChecker == 1)
             return START_DELIM + "NumberBytes" + END_DELIM + toHex(bin);
         else if (byteChecker == 2)
             return START_DELIM + "RepeatedNumberBytes" + END_DELIM + toHex(bin);
         else
             return START_DELIM + protoName + END_DELIM + toHex(bin);
     }
     catch (const std::invalid_argument&) {
         throw;
     }
     catch (const std::exception& ex) {
         throw std::invalid_argument(
             std::string("SerializeToHex failed for type '")
             + typeid(T).name() + "': " + ex.what()
         );
     }
 }
 
 } // namespace EncoderProto
 
 #endif // ENCODER_PROTO_TPP 