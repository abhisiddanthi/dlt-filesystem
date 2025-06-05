#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <string>
#include <dlt/dlt.h>

class Logger {
public:
    Logger();
    ~Logger();

    void init();
    void logData(const std::string& hexData);
    void shutdown();

private:
    DLT_DECLARE_CONTEXT(ctx);
};

#endif 
