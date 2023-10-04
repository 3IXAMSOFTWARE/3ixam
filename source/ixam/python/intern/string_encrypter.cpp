#include <string>
#include <iostream>
#include <iterator>

#include "string_encrypter.h"

template<std::size_t SIZE>
struct hiddenString
{
     short s[SIZE];

     constexpr hiddenString():s{0} { }

     std::string decode() const
     {
      std::string rv;
      rv.reserve(SIZE + 1);
      std::transform(s, s + SIZE - 1, std::back_inserter(rv), [](auto ch) {
        return ch - 1;
      });
      return rv;
     }
};


template<typename T, std::size_t N> constexpr std::size_t sizeCalculate(const T(&)[N])
{
     return N;
}


template<std::size_t SIZE>
constexpr auto encoder(const char str[SIZE])
{
    hiddenString<SIZE> encoded;
  for(std::size_t i = 0; i < SIZE - 1; i++)
        encoded.s[i] = str[i] + 1;
  encoded.s[SIZE - 1] = 0;
    return encoded;
}

#define CRYPTEDSTRING(name, x) constexpr auto name = encoder<sizeCalculate(x)>(x)

char *get_encrypted_password()
{
    CRYPTEDSTRING(str, BUILD_TIME_HASH);
  
    char *encrypted = (char *)malloc(str.decode().size() + 1);

    if (encrypted == NULL) {
      return NULL;
    }

    strcpy(encrypted, str.decode().c_str());

    return encrypted;
}
