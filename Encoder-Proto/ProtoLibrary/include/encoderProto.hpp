// encoderProto.hpp
#ifndef ENCODER_PROTO_HPP
#define ENCODER_PROTO_HPP

#include <iostream>
#include <sstream>
#include <string>
#include <iomanip>
#include <memory>
#include <cstdio>
#include <tuple>
#include <utility>
#include <cstdint>
#include <type_traits>
#include <vector>
#include <unordered_map>
#include <typeinfo>
#include <stdexcept>
#include <algorithm>
#include <cctype>

#include <google/protobuf/message.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/reflection.h>
#include <google/protobuf/util/json_util.h>

#include "../build/logger.pb.h"

namespace EncoderProto {

/**
 * @class Encoder
 * @brief Serializes C++ objects into hex-encoded Protocol Buffer messages.
 *
 * Supported types:
 *  - Primitive scalars: int32_t, int64_t, uint32_t, uint64_t,
 *    float, double, bool, std::string
 *  - Repeated scalars: std::vector<...>
 *  - Nested reflectable types via reflect() → std::tuple<...>
 *  - C++ enums → proto enums
 *  - Raw-byte detection in std::string and std::vector<std::string>
 *
 * All public SerializeToHex() overloads throw std::invalid_argument
 * on unknown type or serialization errors.
 */
class Encoder {
private:
    /**
     * @brief Convert raw binary into its lowercase hexadecimal representation.
     * @param input Raw bytes to encode.
     * @return A hex string (0–9, a–f).
     */
    std::string toHex(const std::string& input);

    /// @name Primitive single-field overloads
    /// @{
    void putValue(int32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(int64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(uint32_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(uint64_t value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(float value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(double value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(bool value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::string& value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);
    /// @}

    /// @name Primitive repeated-field overloads
    /// @{
    void putValue(const std::vector<int32_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<int64_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<uint32_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<uint64_t>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<float>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<double>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<bool>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    void putValue(const std::vector<std::string>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);
    /// @}

    /// @name Nested-message overloads (non-enum)
    /// @{
    /**
     * @brief Serialize a reflectable object into a nested message.
     * @tparam T A user type providing reflect() → std::tuple<...>.
     * @param obj   The object to serialize.
     * @param refl  Reflection interface for the parent message.
     * @param field Descriptor of the nested message field.
     * @param m     Shared pointer to the parent message.
     */
    template <typename T>
    typename std::enable_if<!std::is_enum<T>::value, void>::type
    putValue(const T& obj, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    /**
     * @brief Serialize a vector of reflectable objects as repeated nested messages.
     * @tparam T A user type providing reflect() → std::tuple<...>.
     * @param values The objects to serialize.
     * @param refl   Reflection interface for the parent message.
     * @param field  Descriptor of the repeated nested message field.
     * @param m      Shared pointer to the parent message.
     */
    template <typename T>
    typename std::enable_if<!std::is_enum<T>::value, void>::type
    putValue(const std::vector<T>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);
    /// @}

    /// @name Enum-type overloads
    /// @{
    /**
     * @brief Serialize a C++ enum into a protobuf enum field.
     * @tparam E An enum type.
     * @param value The enum value.
     * @param refl  Reflection interface for the message.
     * @param field Descriptor for the enum field.
     * @param m     Shared pointer to the message.
     */
    template <typename E>
    typename std::enable_if<std::is_enum<E>::value, void>::type
    putValue(E value, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);

    /**
     * @brief Serialize a vector of C++ enums into a repeated protobuf enum field.
     * @tparam E An enum type.
     * @param values The enum values.
     * @param refl   Reflection interface for the message.
     * @param field  Descriptor for the repeated enum field.
     * @param m      Shared pointer to the message.
     */
    template <typename E>
    typename std::enable_if<std::is_enum<E>::value, void>::type
    putValue(const std::vector<E>& values, const google::protobuf::Reflection* refl, const google::protobuf::FieldDescriptor* field, std::shared_ptr<google::protobuf::Message> m);
    /// @}

    /// @name Tuple iteration for reflectable types
    /// @{
    /**
     * @brief Internal helper: iterate over a tuple of fields.
     * @tparam Tuple A std::tuple<...> type.
     * @tparam Is    Compile-time index sequence.
     */
    template <typename Tuple, std::size_t... Is>
    void iterateTuple(const Tuple& t, std::shared_ptr<google::protobuf::Message> m, std::index_sequence<Is...>);

    template <typename Tuple>
    void iterateTuple(const Tuple& t, std::shared_ptr<google::protobuf::Message> m);
    /// @}

    /// @name Raw-byte detection
    /// @{
    /**
     * @brief Catch-all: non-string types are not raw bytes.
     */
    template<typename U>
    static bool isByteString(const U& data);

    /**
     * @brief Detect if a std::string contains non-printable bytes.
     */
    static bool isByteString(const std::string& s);

    /**
     * @brief Catch-all: non-vector<string> are not repeated raw bytes.
     */
    template<typename U>
    static bool isRepeatedByteString(const U& data);

    /**
     * @brief Detect if any element of a vector<string> is raw bytes.
     */
    static bool isRepeatedByteString(const std::vector<std::string>& v);
    /// @}

    /// @brief Reflect a user object into a protobuf Message via reflect().
    template <typename T>
    void fillMessageContents(const T& obj, std::shared_ptr<google::protobuf::Message> m);

    /**
     * @brief Instantiate a protobuf Message by its type name.
     * @param typeName The fully qualified protobuf message name.
     * @return Shared pointer to a new Message, or nullptr if not found.
     */
    std::shared_ptr<google::protobuf::Message>
    createMessageByType(const std::string& typeName);

public:
    /**
     * @brief Serialize data into a named protobuf and hex-encode it.
     *
     * When data is a raw byte string, NumberBytes is chosen automatically.
     *
     * @tparam T Type of the data.
     * @param messageName Protobuf message type name.
     * @param data        The data to serialize.
     * @return Hex string: header + payload.
     * @throws std::invalid_argument on error.
     */
    template <typename T>
    std::string SerializeToHex(const std::string& messageName, const T& data);

    /**
     * @brief Serialize data based on its C++ type mapping and hex-encode.
     *
     * Looks up T in an internal map to find the corresponding protobuf type.
     * Handles raw and repeated byte strings specially.
     *
     * @tparam T Type of the data.
     * @param data The data to serialize.
     * @return Hex string: header + payload.
     * @throws std::invalid_argument on error.
     */
    template <typename T>
    std::string SerializeToHex(const T& data);
};

} // namespace EncoderProto

#include "encoderProto.tpp"
#endif // ENCODER_PROTO_HPP