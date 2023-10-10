/* SPDX-License-Identifier: GPL-2.0-or-later */


#ifndef WITH_PYTHON_MODULE

#  if defined(__linux__) && defined(__GNUC__)
#    define _GNU_SOURCE
#    include <fenv.h>
#  endif

#  if (defined(__APPLE__) && (defined(__i386__) || defined(__x86_64__)))
#    define OSX_SSE_FPE
#    include <xmmintrin.h>
#  endif

#  ifdef WIN32
#    include <float.h>
#    include <windows.h>
#  endif

#  include <errno.h>
#  include <stdlib.h>
#  include <string.h>

#  include "BLI_sys_types.h"

#  ifdef WIN32
#    include "BLI_winstuff.h"
#  endif
#  include "BLI_fileops.h"
#  include "BLI_path_util.h"
#  include "BLI_string.h"
#  include "BLI_system.h"
#  include "BLI_utildefines.h"
#  include BLI_SYSTEM_PID_H

#  include "BKE_appdir.h" /* BKE_tempdir_base */
#  include "BKE_ixam_version.h"
#  include "BKE_global.h"
#  include "BKE_main.h"
#  include "BKE_report.h"
#  include "BKE_context.h"

# include "BPY_extern_run.h"

#  include <signal.h>
#  include <time.h>

#  ifdef WITH_PYTHON
#    include "BPY_extern_python.h" /* BPY_python_backtrace */
#  endif

#  include "creator_intern.h" /* own include */

 #define USE_WRITE_CRASH_IXAM
#  ifdef USE_WRITE_CRASH_IXAM
#    include "BKE_undo_system.h"
#    include "BLO_undofile.h"
#    include "ED_undo.h"
#  endif

/* set breakpoints here when running in debug mode, useful to catch floating point errors */
#  if defined(__linux__) || defined(_WIN32) || defined(OSX_SSE_FPE)
static void sig_handle_fpe(int UNUSED(sig))
{
  fprintf(stderr, "debug: SIGFPE trapped\n");
}
#  endif

/* Handling `Ctrl-C` event in the console. */
static void sig_handle_ixam_esc(int sig)
{
  G.is_break = true; /* forces render loop to read queue, not sure if its needed */

  if (sig == 2) {
    static int count = 0;
    if (count) {
      printf("\nIxam killed\n");
      exit(2);
    }
    printf("\nSent an internal break event. Press ^C again to kill 3IXAM\n");
    count++;
  }
}

static void sig_handle_crash_backtrace(FILE *fp)
{
  fputs("\n# backtrace\n", fp);
  BLI_system_backtrace(fp);
}

static bool saved = false;

static void sig_handle_crash(int signum)
{
  /* Might be called after WM/Main exit, so needs to be careful about NULL-checking before
   * de-referencing. */
  if (!saved) {
    saved = true;
    
    wmWindowManager *wm = G_MAIN ? G_MAIN->wm.first : NULL;
      
    char fname[FILE_MAX];
    char tmp_dir[FILE_MAX];

    time_t t;
    char cur_time[256];
    struct tm *lt;
    
    t = time(NULL);
    lt = localtime(&t);
    
    SNPRINTF(cur_time,
             "%04d-%02d-%02d-%02d-%02d-%02d",
             lt->tm_year + 1900,
             lt->tm_mon + 1,
             lt->tm_mday,
             lt->tm_hour,
             lt->tm_min,
             lt->tm_sec);

    const char *group_dir = BKE_appdir_folder_id(IXAM_SYSTEM_GROUP, NULL);
    if (group_dir == NULL)
      return;
    BLI_path_join(tmp_dir, sizeof(tmp_dir), group_dir, "Library", "Application Support", "3ixam_crashes", cur_time);
    BLI_dir_create_recursive(tmp_dir);

  #  ifdef USE_WRITE_CRASH_IXAM
    if (wm && wm->undo_stack) {
      struct MemFile *memfile = ED_undosys_stack_memfile_get_active(wm->undo_stack);
      if (memfile) {
        BLI_path_join(fname, sizeof(fname), tmp_dir,  "crash.ixam");

        printf("Writing: %s\n", fname);
        fflush(stdout);

        BLO_memfile_write_file(memfile, fname);
      }
    }
  #  endif

    FILE *fp;
    char header[512];
    BLI_path_join(fname, sizeof(fname), tmp_dir, "ixam.crash.txt");
    
    printf("Writing: %s\n", fname);
    fflush(stdout);

  #  ifndef BUILD_DATE
    BLI_snprintf(
        header, sizeof(header), "# " IXAM_VERSION_FMT ", Unknown revision\n", IXAM_VERSION_ARG);
  #  else
    BLI_snprintf(header,
                 sizeof(header),
                 "# " IXAM_VERSION_FMT ", Commit date: %s %s, Hash %s\n",
                 IXAM_VERSION_ARG,
                 build_commit_date,
                 build_commit_time,
                 build_hash);
  #  endif

    /* open the crash log */
    errno = 0;
    fp = BLI_fopen(fname, "wb");
    if (fp == NULL) {
      fprintf(stderr,
              "Unable to save '%s': %s\n",
              fname,
              errno ? strerror(errno) : "Unknown error opening file");
    }
    else {
      if (wm) {
        BKE_report_write_file_fp(fp, &wm->reports, header);
      }

      sig_handle_crash_backtrace(fp);

  #  ifdef WITH_PYTHON
      /* Generate python back-trace if Python is currently active. */
      BPY_python_backtrace(fp);
  #  endif

      fclose(fp);
    }
    
    BLI_path_join(fname, sizeof(fname), tmp_dir,  "sys_info.txt");
  
    bContext *C = CTX_create();
    char run_write_sysinfo[256];
    SNPRINTF(run_write_sysinfo,
             "bpy.utils.write_sysinfo('%s')",
             fname);
    
    printf("Writing: %s\n", fname);
    BPY_run_string_eval(C,
                        (const char *[]){"bpy", NULL},
                        run_write_sysinfo);
  }

  /* Delete content of temp dir! */
  BKE_tempdir_session_purge();

  /* really crash */
  signal(signum, SIG_DFL);
#  ifndef WIN32
  kill(getpid(), signum);
#  else
  TerminateProcess(GetCurrentProcess(), signum);
#  endif
}

#  ifdef WIN32
extern LONG WINAPI windows_exception_handler(EXCEPTION_POINTERS *ExceptionInfo)
{
  /* If this is a stack overflow then we can't walk the stack, so just try to show
   * where the error happened */
  if (ExceptionInfo->ExceptionRecord->ExceptionCode == EXCEPTION_STACK_OVERFLOW) {
    HMODULE mod;
    CHAR modulename[MAX_PATH];
    LPVOID address = ExceptionInfo->ExceptionRecord->ExceptionAddress;
    fprintf(stderr, "Error   : EXCEPTION_STACK_OVERFLOW\n");
    fprintf(stderr, "Address : 0x%p\n", address);
    if (GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, address, &mod)) {
      if (GetModuleFileName(mod, modulename, MAX_PATH)) {
        fprintf(stderr, "Module  : %s\n", modulename);
      }
    }
  }
  else {
    BLI_windows_handle_exception(ExceptionInfo);
    sig_handle_crash(SIGSEGV);
  }

  return EXCEPTION_EXECUTE_HANDLER;
}
#  endif

static void sig_handle_abort(int UNUSED(signum))
{
  /* Delete content of temp dir! */
  BKE_tempdir_session_purge();
}

void main_signal_setup(void)
{
  if (app_state.signal.use_crash_handler) {
#  ifdef WIN32
    SetUnhandledExceptionFilter(windows_exception_handler);
#  else
    /* after parsing args */
    signal(SIGSEGV, sig_handle_crash);
#  endif
  } 

#  ifdef WIN32
  /* Prevent any error mode dialogs from hanging the application. */
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOALIGNMENTFAULTEXCEPT | SEM_NOGPFAULTERRORBOX |
               SEM_NOOPENFILEERRORBOX);
#  endif

  if (app_state.signal.use_abort_handler) {
    signal(SIGABRT, sig_handle_crash);
  }
  
  signal(SIGBUS, sig_handle_crash);
  
}

void main_signal_setup_background(void)
{
  /* for all platforms, even windows has it! */
  BLI_assert(G.background);

  /* Support pressing `Ctrl-C` to close 3IXAM in background-mode.
   * Useful to be able to cancel a render operation. */
  signal(SIGINT, sig_handle_ixam_esc);
}

void main_signal_setup_fpe(void)
{
#  if defined(__linux__) || defined(_WIN32) || defined(OSX_SSE_FPE)
  /* zealous but makes float issues a heck of a lot easier to find!
   * set breakpoints on sig_handle_fpe */
  signal(SIGFPE, sig_handle_fpe);

#    if defined(__linux__) && defined(__GNUC__) && defined(HAVE_FEENABLEEXCEPT)
  feenableexcept(FE_DIVBYZERO | FE_INVALID | FE_OVERFLOW);
#    endif /* defined(__linux__) && defined(__GNUC__) */
#    if defined(OSX_SSE_FPE)
  /* OSX uses SSE for floating point by default, so here
   * use SSE instructions to throw floating point exceptions */
  _MM_SET_EXCEPTION_MASK(_MM_MASK_MASK &
                         ~(_MM_MASK_OVERFLOW | _MM_MASK_INVALID | _MM_MASK_DIV_ZERO));
#    endif /* OSX_SSE_FPE */
#    if defined(_WIN32) && defined(_MSC_VER)
  /* enables all fp exceptions */
  _controlfp_s(NULL, 0, _MCW_EM);
  /* hide the ones we don't care about */
  _controlfp_s(NULL, _EM_DENORMAL | _EM_UNDERFLOW | _EM_INEXACT, _MCW_EM);
#    endif /* _WIN32 && _MSC_VER */
#  endif
}

#endif /* WITH_PYTHON_MODULE */
