#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <string>

using namespace std;

class DLTLogger {
public:
    void init();
    void logData(const string& data);
    void shutdown();
};

#endif 
