

/** \file
 * \ingroup avi
 */

#pragma once

void *avi_converter_from_avi_rgb(AviMovie *movie,
                                 int stream,
                                 unsigned char *buffer,
                                 const size_t *size);
void *avi_converter_to_avi_rgb(AviMovie *movie, int stream, unsigned char *buffer, size_t *size);
