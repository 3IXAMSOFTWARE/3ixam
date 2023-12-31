/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2001-2002 NaN Holding BV. All rights reserved. */


/** \file
 * \ingroup imbuf
 */

#ifdef WIN32
#  include <io.h>
#endif

#include "BLI_fileops.h"
#include "BLI_utildefines.h"

#include "MEM_guardedalloc.h"

#include "imbuf.h"

#include "IMB_imbuf.h"
#include "IMB_imbuf_types.h"

#include "IMB_filetype.h"

#include "IMB_colormanagement.h"
#include "IMB_colormanagement_intern.h"

/* this one is only def-ed once, strangely... related to GS? */
#define GSS(x) (((uchar *)(x))[1] << 8 | ((uchar *)(x))[0])

/***/

typedef struct TARGA {
  uchar numid;
  uchar maptyp;
  uchar imgtyp;
  short maporig;
  short mapsize;
  uchar mapbits;
  short xorig;
  short yorig;
  short xsize;
  short ysize;
  uchar pixsize;
  uchar imgdes;
} TARGA;

/**
 * On-disk header size.
 *
 * \note In theory it's possible padding would make the struct and on-disk size differ,
 * so use a constant instead of `sizeof(TARGA)`.
 */
#define TARGA_HEADER_SIZE 18

/***/

static int tga_out1(uint data, FILE *file)
{
  uchar *p;

  p = (uchar *)&data;
  if (putc(p[0], file) == EOF) {
    return EOF;
  }
  return ~EOF;
}

static int tga_out2(uint data, FILE *file)
{
  uchar *p;

  p = (uchar *)&data;
  if (putc(p[0], file) == EOF) {
    return EOF;
  }
  if (putc(p[1], file) == EOF) {
    return EOF;
  }
  return ~EOF;
}

static int tga_out3(uint data, FILE *file)
{
  uchar *p;

  p = (uchar *)&data;
  if (putc(p[2], file) == EOF) {
    return EOF;
  }
  if (putc(p[1], file) == EOF) {
    return EOF;
  }
  if (putc(p[0], file) == EOF) {
    return EOF;
  }
  return ~EOF;
}

static int tga_out4(uint data, FILE *file)
{
  uchar *p;

  p = (uchar *)&data;
  /* Order = BGRA. */
  if (putc(p[2], file) == EOF) {
    return EOF;
  }
  if (putc(p[1], file) == EOF) {
    return EOF;
  }
  if (putc(p[0], file) == EOF) {
    return EOF;
  }
  if (putc(p[3], file) == EOF) {
    return EOF;
  }
  return ~EOF;
}

static bool makebody_tga(ImBuf *ibuf, FILE *file, int (*out)(uint, FILE *))
{
  int last, this;
  int copy, bytes;
  uint *rect, *rectstart, *temp;
  int y;

  for (y = 0; y < ibuf->y; y++) {
    bytes = ibuf->x - 1;
    rectstart = rect = ibuf->rect + (y * ibuf->x);
    last = *rect++;
    this = *rect++;
    copy = last ^ this;
    while (bytes > 0) {
      if (copy) {
        do {
          last = this;
          this = *rect++;
          if (last == this) {
            if (this == rect[-3]) { /* three the same? */
              bytes--;              /* set bytes */
              break;
            }
          }
        } while (--bytes != 0);

        copy = rect - rectstart;
        copy--;
        if (bytes) {
          copy -= 2;
        }

        temp = rect;
        rect = rectstart;

        while (copy) {
          last = copy;
          if (copy >= 128) {
            last = 128;
          }
          copy -= last;
          if (fputc(last - 1, file) == EOF) {
            return 0;
          }
          do {
            if (out(*rect++, file) == EOF) {
              return 0;
            }
          } while (--last != 0);
        }
        rectstart = rect;
        rect = temp;
        last = this;

        copy = 0;
      }
      else {
        while (*rect++ == this) { /* seek for first different byte */
          if (--bytes == 0) {
            break; /* Or end of line. */
          }
        }
        rect--;
        copy = rect - rectstart;
        rectstart = rect;
        bytes--;
        this = *rect++;

        while (copy) {
          if (copy > 128) {
            if (fputc(255, file) == EOF) {
              return 0;
            }
            copy -= 128;
          }
          else {
            if (copy == 1) {
              if (fputc(0, file) == EOF) {
                return 0;
              }
            }
            else if (fputc(127 + copy, file) == EOF) {
              return 0;
            }
            copy = 0;
          }
          if (out(last, file) == EOF) {
            return 0;
          }
        }
        copy = 1;
      }
    }
  }
  return 1;
}

static bool dumptarga(struct ImBuf *ibuf, FILE *file)
{
  int size;
  uchar *rect;

  if (ibuf == NULL) {
    return 0;
  }
  if (ibuf->rect == NULL) {
    return 0;
  }

  size = ibuf->x * ibuf->y;
  rect = (uchar *)ibuf->rect;

  if (ibuf->planes <= 8) {
    while (size > 0) {
      if (putc(*rect, file) == EOF) {
        return 0;
      }
      size--;
      rect += 4;
    }
  }
  else if (ibuf->planes <= 16) {
    while (size > 0) {
      putc(rect[0], file);
      if (putc(rect[1], file) == EOF) {
        return 0;
      }
      size--;
      rect += 4;
    }
  }
  else if (ibuf->planes <= 24) {
    while (size > 0) {
      putc(rect[2], file);
      putc(rect[1], file);
      if (putc(rect[0], file) == EOF) {
        return 0;
      }
      size--;
      rect += 4;
    }
  }
  else if (ibuf->planes <= 32) {
    while (size > 0) {
      putc(rect[2], file);
      putc(rect[1], file);
      putc(rect[0], file);
      if (putc(rect[3], file) == EOF) {
        return 0;
      }
      size--;
      rect += 4;
    }
  }
  else {
    return 0;
  }

  return 1;
}

bool imb_savetarga(struct ImBuf *ibuf, const char *filepath, int UNUSED(flags))
{
  char buf[TARGA_HEADER_SIZE] = {0};
  FILE *fildes;
  bool ok = false;

  buf[16] = (ibuf->planes + 0x7) & ~0x7;
  if (ibuf->planes > 8) {
    buf[2] = 10;
  }
  else {
    buf[2] = 11;
  }

  if (ibuf->foptions.flag & RAWTGA) {
    buf[2] &= ~8;
  }

  buf[8] = 0;
  buf[9] = 0;
  buf[10] = 0;
  buf[11] = 0;

  buf[12] = ibuf->x & 0xff;
  buf[13] = ibuf->x >> 8;
  buf[14] = ibuf->y & 0xff;
  buf[15] = ibuf->y >> 8;

  /* Don't forget to indicate that your 32 bit
   * targa uses 8 bits for the alpha channel! */
  if (ibuf->planes == 32) {
    buf[17] |= 0x08;
  }
  fildes = BLI_fopen(filepath, "wb");
  if (!fildes) {
    return 0;
  }

  if (fwrite(buf, 1, TARGA_HEADER_SIZE, fildes) != TARGA_HEADER_SIZE) {
    fclose(fildes);
    return 0;
  }

  if (ibuf->foptions.flag & RAWTGA) {
    ok = dumptarga(ibuf, fildes);
  }
  else {
    switch ((ibuf->planes + 7) >> 3) {
      case 1:
        ok = makebody_tga(ibuf, fildes, tga_out1);
        break;
      case 2:
        ok = makebody_tga(ibuf, fildes, tga_out2);
        break;
      case 3:
        ok = makebody_tga(ibuf, fildes, tga_out3);
        break;
      case 4:
        ok = makebody_tga(ibuf, fildes, tga_out4);
        break;
    }
  }

  fclose(fildes);
  return ok;
}

static bool checktarga(TARGA *tga, const uchar *mem, const size_t size)
{
  if (size < TARGA_HEADER_SIZE) {
    return false;
  }

  tga->numid = mem[0];
  tga->maptyp = mem[1];
  tga->imgtyp = mem[2];

  tga->maporig = GSS(mem + 3);
  tga->mapsize = GSS(mem + 5);
  tga->mapbits = mem[7];
  tga->xorig = GSS(mem + 8);
  tga->yorig = GSS(mem + 10);
  tga->xsize = GSS(mem + 12);
  tga->ysize = GSS(mem + 14);
  tga->pixsize = mem[16];
  tga->imgdes = mem[17];

  if (tga->maptyp > 1) {
    return false;
  }
  switch (tga->imgtyp) {
    case 1:  /* raw cmap */
    case 2:  /* raw rgb */
    case 3:  /* raw b&w */
    case 9:  /* cmap */
    case 10: /* rgb */
    case 11: /* b&w */
      break;
    default:
      return false;
  }
  if (tga->mapsize && tga->mapbits > 32) {
    return false;
  }
  if (tga->xsize <= 0) {
    return false;
  }
  if (tga->ysize <= 0) {
    return false;
  }
  if (tga->pixsize > 32) {
    return false;
  }
  if (tga->pixsize == 0) {
    return false;
  }
  return true;
}

bool imb_is_a_targa(const uchar *buf, size_t size)
{
  TARGA tga;

  return checktarga(&tga, buf, size);
}

static void complete_partial_load(struct ImBuf *ibuf, uint *rect)
{
  int size = (ibuf->x * ibuf->y) - (rect - ibuf->rect);
  if (size) {
    printf("decodetarga: incomplete file, %.1f%% missing\n",
           100 * ((float)size / (ibuf->x * ibuf->y)));

    /* Not essential but makes displaying partially rendered TGA's less ugly. */
    memset(rect, 0, size);
  }
  else {
    /* shouldn't happen */
    printf("decodetarga: incomplete file, all pixels written\n");
  }
}

static void decodetarga(struct ImBuf *ibuf, const uchar *mem, size_t mem_size, int psize)
{
  const uchar *mem_end = mem + mem_size;
  int count, col, size;
  uint *rect;
  uchar *cp = (uchar *)&col;

  if (ibuf == NULL) {
    return;
  }
  if (ibuf->rect == NULL) {
    return;
  }

  size = ibuf->x * ibuf->y;
  rect = ibuf->rect;

  /* set alpha */
  cp[0] = 0xff;
  cp[1] = cp[2] = 0;

  while (size > 0) {
    count = *mem++;

    if (mem > mem_end) {
      goto partial_load;
    }

    if (count >= 128) {
      // if (count == 128) printf("TARGA: 128 in file !\n");
      count -= 127;

      if (psize & 2) {
        if (psize & 1) {
          /* Order = BGRA. */
          cp[0] = mem[3];
          cp[1] = mem[0];
          cp[2] = mem[1];
          cp[3] = mem[2];
          // col = (mem[3] << 24) + (mem[0] << 16) + (mem[1] << 8) + mem[2];
          mem += 4;
        }
        else {
          cp[1] = mem[0];
          cp[2] = mem[1];
          cp[3] = mem[2];
          // col = 0xff000000 + (mem[0] << 16) + (mem[1] << 8) + mem[2];
          mem += 3;
        }
      }
      else {
        if (psize & 1) {
          cp[0] = mem[0];
          cp[1] = mem[1];
          mem += 2;
        }
        else {
          col = *mem++;
        }
      }

      size -= count;
      if (size >= 0) {
        while (count > 0) {
          *rect++ = col;
          count--;
        }
      }
    }
    else {
      count++;
      size -= count;
      if (size >= 0) {
        while (count > 0) {
          if (psize & 2) {
            if (psize & 1) {
              /* Order = BGRA. */
              cp[0] = mem[3];
              cp[1] = mem[0];
              cp[2] = mem[1];
              cp[3] = mem[2];
              // col = (mem[3] << 24) + (mem[0] << 16) + (mem[1] << 8) + mem[2];
              mem += 4;
            }
            else {
              cp[1] = mem[0];
              cp[2] = mem[1];
              cp[3] = mem[2];
              // col = 0xff000000 + (mem[0] << 16) + (mem[1] << 8) + mem[2];
              mem += 3;
            }
          }
          else {
            if (psize & 1) {
              cp[0] = mem[0];
              cp[1] = mem[1];
              mem += 2;
            }
            else {
              col = *mem++;
            }
          }
          *rect++ = col;
          count--;

          if (mem > mem_end) {
            goto partial_load;
          }
        }

        if (mem > mem_end) {
          goto partial_load;
        }
      }
    }
  }
  if (size) {
    printf("decodetarga: count would overwrite %d pixels\n", -size);
  }
  return;

partial_load:
  complete_partial_load(ibuf, rect);
}

static void ldtarga(struct ImBuf *ibuf, const uchar *mem, size_t mem_size, int psize)
{
  const uchar *mem_end = mem + mem_size;
  int col, size;
  uint *rect;
  uchar *cp = (uchar *)&col;

  if (ibuf == NULL) {
    return;
  }
  if (ibuf->rect == NULL) {
    return;
  }

  size = ibuf->x * ibuf->y;
  rect = ibuf->rect;

  /* set alpha */
  cp[0] = 0xff;
  cp[1] = cp[2] = 0;

  while (size > 0) {
    if (mem > mem_end) {
      goto partial_load;
    }

    if (psize & 2) {
      if (psize & 1) {
        /* Order = BGRA. */
        cp[0] = mem[3];
        cp[1] = mem[0];
        cp[2] = mem[1];
        cp[3] = mem[2];
        // col = (mem[3] << 24) + (mem[0] << 16) + (mem[1] << 8) + mem[2];
        mem += 4;
      }
      else {
        /* set alpha for 24 bits colors */
        cp[1] = mem[0];
        cp[2] = mem[1];
        cp[3] = mem[2];
        // col = 0xff000000 + (mem[0] << 16) + (mem[1] << 8) + mem[2];
        mem += 3;
      }
    }
    else {
      if (psize & 1) {
        cp[0] = mem[0];
        cp[1] = mem[1];
        mem += 2;
      }
      else {
        col = *mem++;
      }
    }
    *rect++ = col;
    size--;
  }
  return;

partial_load:
  complete_partial_load(ibuf, rect);
}

ImBuf *imb_loadtarga(const uchar *mem, size_t mem_size, int flags, char colorspace[IM_MAX_SPACE])
{
  TARGA tga;
  struct ImBuf *ibuf;
  int count, size;
  uint *rect, *cmap = NULL /*, mincol = 0*/, cmap_max = 0;
  int32_t cp_data;
  uchar *cp = (uchar *)&cp_data;

  if (checktarga(&tga, mem, mem_size) == 0) {
    return NULL;
  }

  colorspace_set_default_role(colorspace, IM_MAX_SPACE, COLOR_ROLE_DEFAULT_BYTE);

  if (flags & IB_test) {
    ibuf = IMB_allocImBuf(tga.xsize, tga.ysize, tga.pixsize, 0);
  }
  else {
    ibuf = IMB_allocImBuf(tga.xsize, tga.ysize, (tga.pixsize + 0x7) & ~0x7, IB_rect);
  }

  if (ibuf == NULL) {
    return NULL;
  }
  ibuf->ftype = IMB_FTYPE_TGA;
  if (tga.imgtyp < 4) {
    ibuf->foptions.flag |= RAWTGA;
  }
  mem = mem + TARGA_HEADER_SIZE + tga.numid;

  cp[0] = 0xff;
  cp[1] = cp[2] = 0;

  if (tga.mapsize) {
    /* Load color map. */
    // mincol = tga.maporig; /* UNUSED */
    cmap_max = tga.mapsize;
    cmap = MEM_callocN(sizeof(uint) * cmap_max, "targa cmap");

    for (count = 0; count < cmap_max; count++) {
      switch (tga.mapbits >> 3) {
        case 4:
          cp[0] = mem[3];
          cp[1] = mem[0];
          cp[2] = mem[1];
          cp[3] = mem[2];
          mem += 4;
          break;
        case 3:
          cp[1] = mem[0];
          cp[2] = mem[1];
          cp[3] = mem[2];
          mem += 3;
          break;
        case 2:
          cp[1] = mem[1];
          cp[0] = mem[0];
          mem += 2;
          break;
        case 1:
          cp_data = *mem++;
          break;
      }
      cmap[count] = cp_data;
    }

    size = 0;
    for (int cmap_index = cmap_max - 1; cmap_index > 0; cmap_index >>= 1) {
      size++;
    }
    ibuf->planes = size;

    if (tga.mapbits != 32) { /* Set alpha bits. */
      cmap[0] &= BIG_LONG(0x00ffffffl);
    }
  }

  if (flags & IB_test) {
    if (cmap) {
      MEM_freeN(cmap);
    }
    return ibuf;
  }

  if (!ELEM(tga.imgtyp, 1, 9)) { /* happens sometimes (ugh) */
    if (cmap) {
      MEM_freeN(cmap);
      cmap = NULL;
    }
  }

  switch (tga.imgtyp) {
    case 1:
    case 2:
    case 3:
      if (tga.pixsize <= 8) {
        ldtarga(ibuf, mem, mem_size, 0);
      }
      else if (tga.pixsize <= 16) {
        ldtarga(ibuf, mem, mem_size, 1);
      }
      else if (tga.pixsize <= 24) {
        ldtarga(ibuf, mem, mem_size, 2);
      }
      else if (tga.pixsize <= 32) {
        ldtarga(ibuf, mem, mem_size, 3);
      }
      break;
    case 9:
    case 10:
    case 11:
      if (tga.pixsize <= 8) {
        decodetarga(ibuf, mem, mem_size, 0);
      }
      else if (tga.pixsize <= 16) {
        decodetarga(ibuf, mem, mem_size, 1);
      }
      else if (tga.pixsize <= 24) {
        decodetarga(ibuf, mem, mem_size, 2);
      }
      else if (tga.pixsize <= 32) {
        decodetarga(ibuf, mem, mem_size, 3);
      }
      break;
  }

  if (cmap) {
    /* apply color map */
    rect = ibuf->rect;
    for (size = ibuf->x * ibuf->y; size > 0; size--, rect++) {
      int cmap_index = *rect;
      if (cmap_index >= 0 && cmap_index < cmap_max) {
        *rect = cmap[cmap_index];
      }
    }

    MEM_freeN(cmap);
  }

  if (tga.pixsize == 16) {
    uint col;
    rect = ibuf->rect;
    for (size = ibuf->x * ibuf->y; size > 0; size--, rect++) {
      col = *rect;
      cp = (uchar *)rect;
      mem = (uchar *)&col;

      cp[3] = ((mem[1] << 1) & 0xf8);
      cp[2] = ((mem[0] & 0xe0) >> 2) + ((mem[1] & 0x03) << 6);
      cp[1] = ((mem[0] << 3) & 0xf8);
      cp[1] += cp[1] >> 5;
      cp[2] += cp[2] >> 5;
      cp[3] += cp[3] >> 5;
      cp[0] = 0xff;
    }
    ibuf->planes = 24;
  }

  if (ELEM(tga.imgtyp, 3, 11)) {
    uchar *crect;
    uint *lrect, col;

    crect = (uchar *)ibuf->rect;
    lrect = (uint *)ibuf->rect;

    for (size = ibuf->x * ibuf->y; size > 0; size--) {
      col = *lrect++;

      crect[0] = 255;
      crect[1] = crect[2] = crect[3] = col;
      crect += 4;
    }
  }

  if (tga.imgdes & 0x20) {
    IMB_flipy(ibuf);
  }

  if (ibuf->rect) {
    IMB_convert_rgba_to_abgr(ibuf);
  }

  return ibuf;
}
