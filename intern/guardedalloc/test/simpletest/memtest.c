

/**
 * Copyright (C) 2001 NaN Technologies B.V.
 * Simple test of memory.
 */

/* To compile run:
 * gcc -DWITH_GUARDEDALLOC -I../../ -I../../../atomic/ memtest.c  ../../intern/mallocn.c -o memtest
 */

/* Number of chunks to test with */
#define NUM_BLOCKS 10

#include "MEM_guardedalloc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void mem_error_cb(const char *errorStr)
{
  fprintf(stderr, "%s", errorStr);
  fflush(stderr);
}

int main(int argc, char *argv[])
{
  int verbose = 0;
  int error_status = 0;
  int retval = 0;
  int *ip;

  void *p[NUM_BLOCKS];
  int i = 0;

  /* ----------------------------------------------------------------- */
  switch (argc) {
    case 2:
      verbose = atoi(argv[1]);
      if (verbose < 0)
        verbose = 0;
      break;
    case 1:
    default:
      verbose = 0;
  }
  if (verbose) {
    fprintf(stderr, "\n*** Simple memory test\n|\n");
  }

  /* ----------------------------------------------------------------- */
  /* Round one, do a normal allocation, and free the blocks again.     */
  /* ----------------------------------------------------------------- */
  /* flush mem lib output to stderr */
  MEM_set_error_callback(mem_error_cb);

  for (i = 0; i < NUM_BLOCKS; i++) {
    int blocksize = 10000;
    char tagstring[1000];
    if (verbose > 1)
      printf("|--* Allocating block %d\n", i);
    sprintf(tagstring, "Memblock no. %d : ", i);
    p[i] = MEM_callocN(blocksize, strdup(tagstring));
  }

  /* report on that */
  if (verbose > 1)
    MEM_printmemlist();

  /* memory is there: test it */
  error_status = MEM_consistency_check();

  if (verbose) {
    if (error_status) {
      fprintf(stderr, "|--* Memory test FAILED\n|\n");
    }
    else {
      fprintf(stderr, "|--* Memory tested as good (as it should be)\n|\n");
    }
  }

  for (i = 0; i < NUM_BLOCKS; i++) {
    MEM_freeN(p[i]);
  }

  /* ----------------------------------------------------------------- */
  /* Round two, do a normal allocation, and corrupt some blocks.       */
  /* ----------------------------------------------------------------- */
  /* Switch off, because it will complain about some things. */
  MEM_set_error_callback(NULL);

  for (i = 0; i < NUM_BLOCKS; i++) {
    int blocksize = 10000;
    char tagstring[1000];
    if (verbose > 1)
      printf("|--* Allocating block %d\n", i);
    sprintf(tagstring, "Memblock no. %d : ", i);
    p[i] = MEM_callocN(blocksize, strdup(tagstring));
  }

  /* Now corrupt a few blocks. */
  ip = (int *)p[5] - 50;
  for (i = 0; i < 1000; i++, ip++)
    *ip = i + 1;
  ip = (int *)p[6];
  *(ip + 10005) = 0;

  retval = MEM_consistency_check();

  /* the test should have failed */
  error_status |= !retval;
  if (verbose) {
    if (retval) {
      fprintf(stderr, "|--* Memory test failed (as it should be)\n");
    }
    else {
      fprintf(stderr, "|--* Memory test FAILED to find corrupted blocks \n");
    }
  }

  for (i = 0; i < NUM_BLOCKS; i++) {
    MEM_freeN(p[i]);
  }

  if (verbose && error_status) {
    fprintf(stderr, "|--* Memory was corrupted\n");
  }
  /* ----------------------------------------------------------------- */
  if (verbose) {
    if (error_status) {
      fprintf(stderr, "|\n|--* Errors were detected\n");
    }
    else {
      fprintf(stderr, "|\n|--* Test exited successfully\n");
    }

    fprintf(stderr, "|\n*** Finished test\n\n");
  }
  return error_status;
}
