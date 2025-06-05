#include "Logger.hpp"
#include <iostream>

using namespace std;

Logger::Logger() {}

Logger::~Logger() {}

void Logger::init() {
    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING("Logger initialized"));
}

void Logger::logData(const string& hexData) {
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(hexData.c_str()));
}

void Logger::shutdown() {
    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();
}
