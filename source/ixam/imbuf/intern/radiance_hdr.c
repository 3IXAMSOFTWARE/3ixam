/* SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup imbuf
 * Radiance High Dynamic Range image file IO
 * For description and code for reading/writing of radiance hdr files
 * by Greg Ward, refer to:
 * http://radsite.lbl.gov/radiance/refer/Notes/picture_format.html
 */

#include "MEM_guardedalloc.h"

#include "BLI_fileops.h"
#include "BLI_utildefines.h"

#include "imbuf.h"

#include "IMB_imbuf.h"
#include "IMB_imbuf_types.h"

#include "IMB_allocimbuf.h"
#include "IMB_filetype.h"

#include "IMB_colormanagement.h"
#include "IMB_colormanagement_intern.h"

/* needed constants */
#define MINELEN 8
#define MAXELEN 0x7fff
#define MINRUN 4 /* minimum run length */
#define RED 0
#define GRN 1
#define BLU 2
#define EXP 3
#define COLXS 128
typedef uchar RGBE[4];
typedef float fCOLOR[3];

/* copy source -> dest */
#define COPY_RGBE(c1, c2) \
  (c2[RED] = c1[RED], c2[GRN] = c1[GRN], c2[BLU] = c1[BLU], c2[EXP] = c1[EXP])

/* read routines */
static const uchar *oldreadcolrs(RGBE *scan, const uchar *mem, int xmax, const uchar *mem_eof)
{
  size_t i, rshift = 0, len = xmax;
  while (len > 0) {
    if (UNLIKELY(mem_eof - mem < 4)) {
      return NULL;
    }
    scan[0][RED] = *mem++;
    scan[0][GRN] = *mem++;
    scan[0][BLU] = *mem++;
    scan[0][EXP] = *mem++;
    if (scan[0][RED] == 1 && scan[0][GRN] == 1 && scan[0][BLU] == 1) {
      for (i = scan[0][EXP] << rshift; i > 0 && len > 0; i--) {
        COPY_RGBE(scan[-1], scan[0]);
        scan++;
        len--;
      }
      rshift += 8;
    }
    else {
      scan++;
      len--;
      rshift = 0;
    }
  }
  return mem;
}

static const uchar *freadcolrs(RGBE *scan, const uchar *mem, int xmax, const uchar *mem_eof)
{
  if (UNLIKELY(mem_eof - mem < 4)) {
    return NULL;
  }

  if (UNLIKELY((xmax < MINELEN) | (xmax > MAXELEN))) {
    return oldreadcolrs(scan, mem, xmax, mem_eof);
  }

  int val = *mem++;
  if (val != 2) {
    return oldreadcolrs(scan, mem - 1, xmax, mem_eof);
  }

  scan[0][GRN] = *mem++;
  scan[0][BLU] = *mem++;

  val = *mem++;

  if (scan[0][GRN] != 2 || scan[0][BLU] & 128) {
    scan[0][RED] = 2;
    scan[0][EXP] = val;
    return oldreadcolrs(scan + 1, mem, xmax - 1, mem_eof);
  }

  if (UNLIKELY(((scan[0][BLU] << 8) | val) != xmax)) {
    return NULL;
  }

  for (size_t i = 0; i < 4; i++) {
    if (UNLIKELY(mem_eof - mem < 2)) {
      return NULL;
    }
    for (size_t j = 0; j < xmax;) {
      int code = *mem++;
      if (code > 128) {
        code &= 127;
        if (UNLIKELY(code + j > xmax)) {
          return NULL;
        }
        val = *mem++;
        while (code--) {
          scan[j++][i] = (uchar)val;
        }
      }
      else {
        if (UNLIKELY(mem_eof - mem < code)) {
          return NULL;
        }
        if (UNLIKELY(code + j > xmax)) {
          return NULL;
        }
        while (code--) {
          scan[j++][i] = *mem++;
        }
      }
    }
  }

  return mem;
}

/* helper functions */

/* rgbe -> float color */
static void RGBE2FLOAT(RGBE rgbe, fCOLOR fcol)
{
  if (rgbe[EXP] == 0) {
    fcol[RED] = fcol[GRN] = fcol[BLU] = 0;
  }
  else {
    float f = ldexp(1.0, rgbe[EXP] - (COLXS + 8));
    fcol[RED] = f * (rgbe[RED] + 0.5f);
    fcol[GRN] = f * (rgbe[GRN] + 0.5f);
    fcol[BLU] = f * (rgbe[BLU] + 0.5f);
  }
}

/* float color -> rgbe */
static void FLOAT2RGBE(const fCOLOR fcol, RGBE rgbe)
{
  int e;
  float d = (fcol[RED] > fcol[GRN]) ? fcol[RED] : fcol[GRN];
  if (fcol[BLU] > d) {
    d = fcol[BLU];
  }
  if (d <= 1e-32f) {
    rgbe[RED] = rgbe[GRN] = rgbe[BLU] = rgbe[EXP] = 0;
  }
  else {
    d = (float)frexp(d, &e) * 256.0f / d;
    rgbe[RED] = (uchar)(fcol[RED] * d);
    rgbe[GRN] = (uchar)(fcol[GRN] * d);
    rgbe[BLU] = (uchar)(fcol[BLU] * d);
    rgbe[EXP] = (uchar)(e + COLXS);
  }
}

/* ImBuf read */

bool imb_is_a_hdr(const uchar *buf, const size_t size)
{
  /* NOTE: `#?RADIANCE` is used by other programs such as `ImageMagik`,
   * Although there are some files in the wild that only use `#?` (from looking online).
   * If this is ever a problem we could check for the longer header since this is part of the spec.
   *
   * We could check `32-bit_rle_rgbe` or `32-bit_rle_xyze` too since this is part of the format.
   * Currently this isn't needed.
   *
   * See: http://paulbourke.net/dataformats/pic/
   */
  const uchar magic[2] = {'#', '?'};
  if (size < sizeof(magic)) {
    return false;
  }
  return memcmp(buf, magic, sizeof(magic)) == 0;
}

struct ImBuf *imb_loadhdr(const uchar *mem, size_t size, int flags, char colorspace[IM_MAX_SPACE])
{
  struct ImBuf *ibuf;
  RGBE *sline;
  fCOLOR fcol;
  float *rect_float;
  int found = 0;
  int width = 0, height = 0;
  const uchar *ptr, *mem_eof = mem + size;
  char oriY[3], oriX[3];

  if (!imb_is_a_hdr(mem, size)) {
    return NULL;
  }

  colorspace_set_default_role(colorspace, IM_MAX_SPACE, COLOR_ROLE_DEFAULT_FLOAT);

  /* find empty line, next line is resolution info */
  size_t x;
  for (x = 1; x < size; x++) {
    if ((mem[x - 1] == '\n') && (mem[x] == '\n')) {
      found = 1;
      break;
    }
  }

  if ((found && (x < (size - 1))) == 0) {
    /* Data not found! */
    return NULL;
  }

  x++;

  /* sscanf requires a null-terminated buffer argument */
  char buf[32] = {0};
  memcpy(buf, &mem[x], MIN2(sizeof(buf) - 1, size - x));

  if (sscanf(buf, "%2s %d %2s %d", (char *)&oriY, &height, (char *)&oriX, &width) != 4) {
    return NULL;
  }

  if (width < 1 || height < 1) {
    return NULL;
  }

  /* Checking that width x height does not extend past mem_eof is not easily possible
   * since the format uses RLE compression. Can cause excessive memory allocation to occur. */

  /* find end of this line, data right behind it */
  ptr = (const uchar *)strchr((const char *)&mem[x], '\n');
  if (ptr == NULL || ptr >= mem_eof) {
    return NULL;
  }
  ptr++;

  if (flags & IB_test) {
    ibuf = IMB_allocImBuf(width, height, 32, 0);
  }
  else {
    ibuf = IMB_allocImBuf(width, height, 32, (flags & IB_rect) | IB_rectfloat);
  }

  if (UNLIKELY(ibuf == NULL)) {
    return NULL;
  }

  ibuf->ftype = IMB_FTYPE_RADHDR;

  if (flags & IB_alphamode_detect) {
    ibuf->flags |= IB_alphamode_premul;
  }

  if (flags & IB_test) {
    return ibuf;
  }

  /* read in and decode the actual data */
  sline = (RGBE *)MEM_mallocN(sizeof(*sline) * width, __func__);
  rect_float = ibuf->rect_float;

  for (size_t y = 0; y < height; y++) {
    ptr = freadcolrs(sline, ptr, width, mem_eof);
    if (ptr == NULL) {
      printf("WARNING! HDR decode error, image may be just truncated, or completely wrong...\n");
      break;
    }
    for (x = 0; x < width; x++) {
      /* Convert to LDR. */
      RGBE2FLOAT(sline[x], fcol);
      *rect_float++ = fcol[RED];
      *rect_float++ = fcol[GRN];
      *rect_float++ = fcol[BLU];
      *rect_float++ = 1.0f;
    }
  }
  MEM_freeN(sline);
  if (oriY[0] == '-') {
    IMB_flipy(ibuf);
  }

  if (flags & IB_rect) {
    IMB_rect_from_float(ibuf);
  }

  return ibuf;
}

/* ImBuf write */
static int fwritecolrs(
    FILE *file, int width, int channels, const uchar *ibufscan, const float *fpscan)
{
  int beg, c2, count = 0;
  fCOLOR fcol;
  RGBE rgbe, *rgbe_scan;

  if (UNLIKELY((ibufscan == NULL) && (fpscan == NULL))) {
    return 0;
  }

  rgbe_scan = (RGBE *)MEM_mallocN(sizeof(RGBE) * width, "radhdr_write_tmpscan");

  /* Convert scan-line. */
  for (size_t i = 0, j = 0; i < width; i++) {
    if (fpscan) {
      fcol[RED] = fpscan[j];
      fcol[GRN] = (channels >= 2) ? fpscan[j + 1] : fpscan[j];
      fcol[BLU] = (channels >= 3) ? fpscan[j + 2] : fpscan[j];
    }
    else {
      fcol[RED] = (float)ibufscan[j] / 255.0f;
      fcol[GRN] = (float)((channels >= 2) ? ibufscan[j + 1] : ibufscan[j]) / 255.0f;
      fcol[BLU] = (float)((channels >= 3) ? ibufscan[j + 2] : ibufscan[j]) / 255.0f;
    }
    FLOAT2RGBE(fcol, rgbe);
    COPY_RGBE(rgbe, rgbe_scan[i]);
    j += channels;
  }

  if ((width < MINELEN) | (width > MAXELEN)) { /* OOBs, write out flat */
    int x = fwrite((char *)rgbe_scan, sizeof(RGBE), width, file) - width;
    MEM_freeN(rgbe_scan);
    return x;
  }
  /* put magic header */
  putc(2, file);
  putc(2, file);
  putc((uchar)(width >> 8), file);
  putc((uchar)(width & 255), file);
  /* put components separately */
  for (size_t i = 0; i < 4; i++) {
    for (size_t j = 0; j < width; j += count) { /* find next run */
      for (beg = j; beg < width; beg += count) {
        for (count = 1; (count < 127) && ((beg + count) < width) &&
                        (rgbe_scan[beg + count][i] == rgbe_scan[beg][i]);
             count++) {
          /* pass */
        }
        if (count >= MINRUN) {
          break; /* long enough */
        }
      }
      if (((beg - j) > 1) && ((beg - j) < MINRUN)) {
        c2 = j + 1;
        while (rgbe_scan[c2++][i] == rgbe_scan[j][i]) {
          if (c2 == beg) { /* short run */
            putc((uchar)(128 + beg - j), file);
            putc((uchar)(rgbe_scan[j][i]), file);
            j = beg;
            break;
          }
        }
      }
      while (j < beg) { /* write out non-run */
        if ((c2 = beg - j) > 128) {
          c2 = 128;
        }
        putc((uchar)(c2), file);
        while (c2--) {
          putc(rgbe_scan[j++][i], file);
        }
      }
      if (count >= MINRUN) { /* write out run */
        putc((uchar)(128 + count), file);
        putc(rgbe_scan[beg][i], file);
      }
      else {
        count = 0;
      }
    }
  }
  MEM_freeN(rgbe_scan);
  return (ferror(file) ? -1 : 0);
}

static void writeHeader(FILE *file, int width, int height)
{
  fprintf(file, "#?RADIANCE");
  fputc(10, file);
  fprintf(file, "# %s", "Created with 3IXAM");
  fputc(10, file);
  fprintf(file, "EXPOSURE=%25.13f", 1.0);
  fputc(10, file);
  fprintf(file, "FORMAT=32-bit_rle_rgbe");
  fputc(10, file);
  fputc(10, file);
  fprintf(file, "-Y %d +X %d", height, width);
  fputc(10, file);
}

bool imb_savehdr(struct ImBuf *ibuf, const char *filepath, int flags)
{
  FILE *file = BLI_fopen(filepath, "wb");
  float *fp = NULL;
  size_t width = ibuf->x, height = ibuf->y;
  uchar *cp = NULL;

  (void)flags; /* unused */

  if (file == NULL) {
    return 0;
  }

  writeHeader(file, width, height);

  if (ibuf->rect) {
    cp = (uchar *)ibuf->rect + ibuf->channels * (height - 1) * width;
  }
  if (ibuf->rect_float) {
    fp = ibuf->rect_float + ibuf->channels * (height - 1) * width;
  }

  for (size_t y = 0; y < height; y++) {
    if (fwritecolrs(file, width, ibuf->channels, cp, fp) < 0) {
      fclose(file);
      printf("HDR write error\n");
      return 0;
    }
    if (cp) {
      cp -= ibuf->channels * width;
    }
    if (fp) {
      fp -= ibuf->channels * width;
    }
  }

  fclose(file);
  return 1;
}
