/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * The Original Code is Copyright (C) 2001-2002 by NaN Holding BV.
 * All rights reserved.
 */

/** \file
 * \ingroup encrypt
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <time.h>
#include <errno.h>
#include <fcntl.h>

#ifdef _WIN32
# include <direct.h>
# include <io.h>
#else
# include <unistd.h>
# include <utime.h>
# include <sys/types.h>
# include <sys/stat.h>
#endif

#include "../python/intern/string_encrypter.h"
 
#include "zip.h"
#include "unzip.h"

#ifdef _WIN32
        #define USEWIN32IOAPI
        #include "iowin32.h"
#endif

static const int WRITEBUFFERSIZE = 16384;
static const int MAXFILENAME = 1024;

#ifdef __APPLE__
// In darwin and perhaps other BSD variants off_t is a 64 bit value, hence no need for specific 64 bit functions
#define FOPEN_FUNC(filename, mode) fopen(filename, mode)
#define FTELLO_FUNC(stream) ftello(stream)
#define FSEEKO_FUNC(stream, offset, origin) fseeko(stream, offset, origin)
#else
#define FOPEN_FUNC(filename, mode) fopen64(filename, mode)
#define FTELLO_FUNC(stream) ftello64(stream)
#define FSEEKO_FUNC(stream, offset, origin) fseeko64(stream, offset, origin)
#endif

#ifdef _WIN32
static int filetime(f, tmzip, dt)
    const char *f;          /* name of file to get info on */
    tm_zip *tmzip;             /* return value: access, modific. and creation times */
    uLong *dt;             /* dostime */
{
  int ret = 0;
  {
      FILETIME ftLocal;
      HANDLE hFind;
      WIN32_FIND_DATAA ff32;

      hFind = FindFirstFileA(f,&ff32);
      if (hFind != INVALID_HANDLE_VALUE)
      {
        FileTimeToLocalFileTime(&(ff32.ftLastWriteTime),&ftLocal);
        FileTimeToDosDateTime(&ftLocal,((LPWORD)dt)+1,((LPWORD)dt)+0);
        FindClose(hFind);
        ret = 1;
      }
  }
  return ret;
}
#else
#if defined(unix) || defined(__APPLE__)
static int filetime(f, tmzip, dt)
    const char *f;         /* name of file to get info on */
    tm_zip *tmzip;         /* return value: access, modific. and creation times */
    uLong *dt;             /* dostime */
{
  (void)dt;
  int ret=0;
  struct stat s;        /* results of stat() */
  struct tm* filedate;
  time_t tm_t=0;

  if (strcmp(f,"-")!=0)
  {
    char name[MAXFILENAME+1];
    size_t len = strlen(f);
    if (len > MAXFILENAME)
      len = MAXFILENAME;

    strncpy(name, f,MAXFILENAME-1);
    /* strncpy doesnt append the trailing NULL, of the string is too long. */
    name[ MAXFILENAME ] = '\0';

    if (name[len - 1] == '/')
      name[len - 1] = '\0';
    /* not all systems allow stat'ing a file with / appended */
    if (stat(name,&s)==0)
    {
      tm_t = s.st_mtime;
      ret = 1;
    }
  }
  filedate = localtime(&tm_t);

  tmzip->tm_sec  = filedate->tm_sec;
  tmzip->tm_min  = filedate->tm_min;
  tmzip->tm_hour = filedate->tm_hour;
  tmzip->tm_mday = filedate->tm_mday;
  tmzip->tm_mon  = filedate->tm_mon ;
  tmzip->tm_year = filedate->tm_year;

  return ret;
}
#else
uLong filetime(f, tmzip, dt)
    const char *f;          /* name of file to get info on */
    tm_zip *tmzip;             /* return value: access, modific. and creation times */
    uLong *dt;             /* dostime */
{
    return 0;
}
#endif
#endif

static int check_exist_file(filename)
    const char* filename;
{
    FILE* ftestexist;
    int ret = 1;
    ftestexist = FOPEN_FUNC(filename,"rb");
    if (ftestexist==NULL)
        ret = 0;
    else
        fclose(ftestexist);
    return ret;
}

/* calculate the CRC32 of a file,
   because to encrypt a file, we need known the CRC32 of the file before */
static int getFileCrc(const char* filepath,void*buf,unsigned long size_buf,unsigned long* result_crc)
{
   unsigned long calculate_crc=0;
   int err=ZIP_OK;
   FILE * fin = FOPEN_FUNC(filepath,"rb");

   unsigned long size_read = 0;
   /* unsigned long total_read = 0; */
   if (fin==NULL)
   {
       err = ZIP_ERRNO;
   }

    if (err == ZIP_OK)
        do
        {
            err = ZIP_OK;
            size_read = fread(buf,1,size_buf,fin);
            if (size_read < size_buf)
                if (feof(fin)==0)
            {
                printf("error in reading %s\n",filepath);
                err = ZIP_ERRNO;
            }

            if (size_read>0)
                calculate_crc = crc32_z(calculate_crc,buf,size_read);
            /* total_read += size_read; */

        } while ((err == ZIP_OK) && (size_read>0));

    if (fin)
        fclose(fin);

    *result_crc=calculate_crc;
    printf("file %s crc %lx\n", filepath, calculate_crc);
    return err;
}

static int isLargeFile(const char* filepath)
{
  int largeFile = 0;
  ZPOS64_T pos = 0;
  FILE* pFile = FOPEN_FUNC(filepath, "rb");

  if(pFile != NULL)
  {
    FSEEKO_FUNC(pFile, 0, SEEK_END);
    pos = (ZPOS64_T)FTELLO_FUNC(pFile);

                printf("File : %s is %lld bytes\n", filepath, pos);

    if(pos >= 0xffffffff)
     largeFile = 1;

                fclose(pFile);
  }

 return largeFile;
}

static inline char* path_separator() {
  #ifdef _WIN32
    return "\\";
  #else
    return "/";
  #endif
}

static inline int str_ends_with(const char* s, const char* suffix) {
  int len_s = strlen(s);
  int len_suffix = strlen(suffix);
  
  if (len_suffix > len_s) {
    return 0;
  }

  for (int i = 1; i <= len_suffix; i++) {
    if (s[len_s - i] != suffix[len_suffix - i]) {
      return 0;
    }
  }

  return 1;
}

static zipFile target_zip_file;
static void* buf = NULL;
static size_t size_buf = 0;
static char* root_dir_path = NULL;
static const char *zip_archive_password = NULL;

static void encrypt_file(const char* filepath, const char* filenameinzip) {
  printf("encrypting %s\n", filepath);

  int err = 0;
  FILE * fin;
  size_t size_read;
  const char* savefilenameinzip;
  zip_fileinfo zi;
  unsigned long crcFile = 0;
  int zip64 = 0;
  int opt_compress_level = Z_DEFAULT_COMPRESSION;
  
  const char* password = zip_archive_password;

  zi.tmz_date.tm_sec = 
  zi.tmz_date.tm_min = 
  zi.tmz_date.tm_hour =
  zi.tmz_date.tm_mday = 
  zi.tmz_date.tm_mon = 
  zi.tmz_date.tm_year = 0;
  zi.dosDate = 0;
  zi.internal_fa = 0;
  zi.external_fa = 0;
  filetime(filepath, &zi.tmz_date, &zi.dosDate);

  if ((password != NULL) && (err==ZIP_OK)) {  
    err = getFileCrc(filepath, buf, size_buf, &crcFile);
  }

  zip64 = isLargeFile(filepath);

  /* The path name saved, should not include a leading slash. */
  /*if it did, windows/xp and dynazip couldn't read the zip file. */
  savefilenameinzip = filenameinzip;
  while( savefilenameinzip[0] == '\\' || savefilenameinzip[0] == '/' ) {
      savefilenameinzip++;
  }

  /**/
  err = zipOpenNewFileInZip3_64(target_zip_file, savefilenameinzip, &zi,
                    NULL,0,NULL,0,NULL /* comment*/,
                    (opt_compress_level != 0) ? Z_DEFLATED : 0,
                    opt_compress_level,0,
                    /* -MAX_WBITS, DEF_MEM_LEVEL, Z_DEFAULT_STRATEGY, */
                    -MAX_WBITS, DEF_MEM_LEVEL, Z_DEFAULT_STRATEGY,
                    password,crcFile, zip64);

  if (err != ZIP_OK) {
    printf("error in opening %s in zipfile\n",filepath);
  } else {
    fin = FOPEN_FUNC(filepath,"rb");
    if (fin==NULL) {
      err=ZIP_ERRNO;
      printf("error in opening %s for reading\n", filepath);
    }
  }

  if (err == ZIP_OK) {
    do {
      err = ZIP_OK;
      size_read = fread(buf,1,size_buf,fin);
      if (size_read < size_buf) {
        if (feof(fin)==0) {
          printf("error in reading %s\n",filepath);
          err = ZIP_ERRNO;
        }
      }

      if (size_read>0) {
        err = zipWriteInFileInZip(target_zip_file, buf, (unsigned)size_read);
        if (err<0) {
          printf("error in writing %s in the zipfile\n", filenameinzip);
        }
      }
    } while ((err == ZIP_OK) && (size_read>0));
  }

  if (fin) {
    fclose(fin);
  }

  if (err<0) {
    err=ZIP_ERRNO;
  } else {
    err = zipCloseFileInZip(target_zip_file);
    if (err!=ZIP_OK)
      printf("error in closing %s in the zipfile\n", filenameinzip);
  }
}

static void iterate_files_and_encrypt(const char* dirpath) {
  DIR *dir;
  struct dirent *dir_entry;
  dir = opendir(dirpath);
  if (!dir) return;

  while ((dir_entry = readdir(dir)) != NULL) {
    if (strcmp(dir_entry->d_name, ".") == 0) continue;
    if (strcmp(dir_entry->d_name, "..") == 0) continue;
    
    if (dir_entry->d_type == DT_REG) {
      char* filepath = malloc(MAXFILENAME * sizeof(char));
      strcpy(filepath, dirpath);
      strcat(filepath, dir_entry->d_name);

      const char* filenameinzip = filepath + strlen(root_dir_path);

      encrypt_file(filepath, filenameinzip);
      
      free(filepath);
    }

    if (dir_entry->d_type == DT_DIR) {
      
      char* subdirpath = malloc(MAXFILENAME * sizeof(char));
      strcpy(subdirpath, dirpath);
      strcat(subdirpath, dir_entry->d_name);
      strcat(subdirpath, path_separator());

      iterate_files_and_encrypt(subdirpath);

      free(subdirpath);
    }
  }
  closedir(dir);
  
}

int main(int argc, char **argv)
{
  // encrypt "/Users/ingame/Documents/recursive_encrypt_test/" "/Users/ingame/Documents/zipencryptest.zip" 
  if (argc < 2) {
    printf("Usage: encrypt <directory_from> <data_file_to>\n");
    return 1;
  }

  // fix directory_from
  // add separator if needed
  char* directory_from = malloc(MAXFILENAME * sizeof(char));
  strcpy(directory_from, argv[1]);
  if (!str_ends_with(directory_from, path_separator())) {
    strcat(directory_from, path_separator());
  }

  char *password = get_encrypted_password();
  zip_archive_password = password;

  printf("Archive password = %s\n", zip_archive_password);

  size_buf = WRITEBUFFERSIZE;
  buf = (void*)malloc(size_buf);
  if (buf == NULL) {
      printf("Error allocating memory\n");
      return ZIP_INTERNALERROR;
  }

  target_zip_file = zipOpen(argv[2], APPEND_STATUS_CREATE);
  root_dir_path = directory_from;

  iterate_files_and_encrypt(root_dir_path);

  int err_zip_close = zipClose(target_zip_file, "");
  if (err_zip_close != ZIP_OK) {
    printf("error in closing encrypted zipfile\n");
  }

  free(buf);
  free(directory_from);
  
  free(password);
  password = NULL;

  return 0;
}

#undef FOPEN_FUNC
#undef FTELLO_FUNC
#undef FSEEKO_FUNC