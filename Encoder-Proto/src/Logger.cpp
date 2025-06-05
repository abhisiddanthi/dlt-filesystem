#include "Logger.hpp"
#include <dlt/dlt.h>

using namespace std;

DLT_DECLARE_CONTEXT(ctx);


void DLTLogger::init() {
    DLT_REGISTER_APP("SWAV", "Sine Wave Encoder");
    DLT_REGISTER_CONTEXT(ctx, "SWC1", "Sine Wave Context");
}

void DLTLogger::logData(const string& data) {
    DLT_LOG(ctx, DLT_LOG_INFO, DLT_STRING(data.c_str()));
}

void DLTLogger::shutdown() {
    DLT_UNREGISTER_CONTEXT(ctx);
    DLT_UNREGISTER_APP();
}
