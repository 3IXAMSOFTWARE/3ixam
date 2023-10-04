
# turn everything OFF except for python which defaults to ON
# and is needed for the UI
#
# Example usage:
#   cmake -C../ixam/build_files/cmake/config/ixam_lite.cmake  ../ixam
#

set(WITH_ALEMBIC             OFF CACHE BOOL "" FORCE)
set(WITH_AUDASPACE           OFF CACHE BOOL "" FORCE)
set(WITH_IXAM_THUMBNAILER OFF CACHE BOOL "" FORCE)
set(WITH_BOOST               OFF CACHE BOOL "" FORCE)
set(WITH_BUILDINFO           OFF CACHE BOOL "" FORCE)
set(WITH_BULLET              OFF CACHE BOOL "" FORCE)
set(WITH_CODEC_AVI           OFF CACHE BOOL "" FORCE)
set(WITH_CODEC_FFMPEG        OFF CACHE BOOL "" FORCE)
set(WITH_CODEC_SNDFILE       OFF CACHE BOOL "" FORCE)
set(WITH_COMPOSITOR_CPU      OFF CACHE BOOL "" FORCE)
set(WITH_COREAUDIO           OFF CACHE BOOL "" FORCE)
set(WITH_CYCLES              OFF CACHE BOOL "" FORCE)
set(WITH_DRACO               OFF CACHE BOOL "" FORCE)
set(WITH_FFTW3               OFF CACHE BOOL "" FORCE)
set(WITH_FREESTYLE           OFF CACHE BOOL "" FORCE)
set(WITH_GMP                 OFF CACHE BOOL "" FORCE)
set(WITH_HARU                OFF CACHE BOOL "" FORCE)
set(WITH_IK_ITASC            OFF CACHE BOOL "" FORCE)
set(WITH_IK_SOLVER           OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_CINEON        OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_DDS           OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_HDR           OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_OPENEXR       OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_OPENJPEG      OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_TIFF          OFF CACHE BOOL "" FORCE)
set(WITH_IMAGE_WEBP          OFF CACHE BOOL "" FORCE)
set(WITH_INPUT_IME           OFF CACHE BOOL "" FORCE)
set(WITH_INPUT_NDOF          OFF CACHE BOOL "" FORCE)
set(WITH_INTERNATIONAL       OFF CACHE BOOL "" FORCE)
set(WITH_IO_STL              OFF CACHE BOOL "" FORCE)
set(WITH_IO_WAVEFRONT_OBJ    OFF CACHE BOOL "" FORCE)
set(WITH_IO_GPENCIL          OFF CACHE BOOL "" FORCE)
set(WITH_JACK                OFF CACHE BOOL "" FORCE)
set(WITH_LIBMV               OFF CACHE BOOL "" FORCE)
set(WITH_LLVM                OFF CACHE BOOL "" FORCE)
set(WITH_LZMA                OFF CACHE BOOL "" FORCE)
set(WITH_LZO                 OFF CACHE BOOL "" FORCE)
set(WITH_MOD_FLUID           OFF CACHE BOOL "" FORCE)
set(WITH_MOD_OCEANSIM        OFF CACHE BOOL "" FORCE)
set(WITH_MOD_REMESH          OFF CACHE BOOL "" FORCE)
set(WITH_NANOVDB             OFF CACHE BOOL "" FORCE)
set(WITH_OPENAL              OFF CACHE BOOL "" FORCE)
set(WITH_OPENCOLLADA         OFF CACHE BOOL "" FORCE)
set(WITH_OPENCOLORIO         OFF CACHE BOOL "" FORCE)
set(WITH_OPENIMAGEDENOISE    OFF CACHE BOOL "" FORCE)
set(WITH_OPENIMAGEIO         OFF CACHE BOOL "" FORCE)
set(WITH_OPENMP              OFF CACHE BOOL "" FORCE)
set(WITH_OPENSUBDIV          OFF CACHE BOOL "" FORCE)
set(WITH_OPENVDB             OFF CACHE BOOL "" FORCE)
set(WITH_POTRACE             OFF CACHE BOOL "" FORCE)
set(WITH_PUGIXML             OFF CACHE BOOL "" FORCE)
set(WITH_PULSEAUDIO          OFF CACHE BOOL "" FORCE)
set(WITH_QUADRIFLOW          OFF CACHE BOOL "" FORCE)
set(WITH_SDL                 OFF CACHE BOOL "" FORCE)
set(WITH_TBB                 OFF CACHE BOOL "" FORCE)
set(WITH_USD                 OFF CACHE BOOL "" FORCE)
set(WITH_WASAPI              OFF CACHE BOOL "" FORCE)
set(WITH_XR_OPENXR           OFF CACHE BOOL "" FORCE)

if(UNIX AND NOT APPLE)
  set(WITH_GHOST_XDND          OFF CACHE BOOL "" FORCE)
  set(WITH_X11_XINPUT          OFF CACHE BOOL "" FORCE)
  set(WITH_X11_XF86VMODE       OFF CACHE BOOL "" FORCE)
endif()