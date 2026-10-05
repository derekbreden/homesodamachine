#pragma once
#include <cstdio>
#include <cstdlib>
#define CHECK(expression) do { if (!(expression)) { \
    std::fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #expression); \
    std::abort(); } } while (false)
