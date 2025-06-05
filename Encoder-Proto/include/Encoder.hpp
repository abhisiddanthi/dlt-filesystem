#ifndef ENCODER_HPP
#define ENCODER_HPP

#include <string>
#include "sine_wave.pb.h"

using namespace std;

template <typename T>
class Encoder {
public:
    virtual ~Encoder() = default;
    virtual string encode(const T& data) = 0;
};

template <typename T>
class ProtoEncoder : public Encoder<T> {
public:
    string encode(const T& data) override;
};

#include "Encoder.tpp"

#endif
