

#ifndef __SDL_EW_H__
#define __SDL_EW_H__

#ifdef __cplusplus
extern "C" {
#endif

enum {
  SDLEW_SUCCESS = 0,
  SDLEW_ERROR_OPEN_FAILED = -1,
  SDLEW_ERROR_ATEXIT_FAILED = -2,
  SDLEW_ERROR_VERSION = -3,
};

int sdlewInit(void);

#ifdef __cplusplus
}
#endif

#endif  /* __SDL_EW_H__ */
