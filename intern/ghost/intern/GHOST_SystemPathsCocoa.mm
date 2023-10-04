

#import <Foundation/Foundation.h>

#include "GHOST_Debug.h"
#include "GHOST_SystemPathsCocoa.h"

NSString *IXAM_GROUP_ID = @"group.5RR29LCW2T.testing.group";

#pragma mark initialization/finalization

GHOST_SystemPathsCocoa::GHOST_SystemPathsCocoa()
{
}

GHOST_SystemPathsCocoa::~GHOST_SystemPathsCocoa()
{
}

#pragma mark Base directories retrieval

static const char *GetApplicationSupportDir(const char *versionstr,
                                            const NSSearchPathDomainMask mask,
                                            char *tempPath,
                                            const std::size_t len_tempPath)
{
  @autoreleasepool {
    const NSArray *const paths = NSSearchPathForDirectoriesInDomains(
        NSApplicationSupportDirectory, mask, YES);

    if ([paths count] == 0) {
      return NULL;
    }
    const NSString *const basePath = [paths objectAtIndex:0];

    snprintf(tempPath,
             len_tempPath,
             "%s/3ixam/%s",
             [basePath cStringUsingEncoding:NSASCIIStringEncoding],
             versionstr);
  }
  return tempPath;
}

const char *GHOST_SystemPathsCocoa::getSystemDir(int version, const char *versionstr) const
{
  static char tempPath[512] = "";
  if (version == 0 && versionstr == NULL)
  {
    NSURL *fileManagerURL = [[NSFileManager defaultManager] containerURLForSecurityApplicationGroupIdentifier:IXAM_GROUP_ID];
    const char *path = [fileManagerURL.path UTF8String];
    snprintf(tempPath,
             sizeof(tempPath),
             "%s",
             path);
    return tempPath;
  }
  return GetApplicationSupportDir(versionstr, NSLocalDomainMask, tempPath, sizeof(tempPath));
}

const char *GHOST_SystemPathsCocoa::getUserDir(int, const char *versionstr) const
{
  static char tempPath[512] = "";
  return GetApplicationSupportDir(versionstr, NSUserDomainMask, tempPath, sizeof(tempPath));
}

const char *GHOST_SystemPathsCocoa::getUserSpecialDir(GHOST_TUserSpecialDirTypes type) const
{
  static char tempPath[512] = "";
  @autoreleasepool {
    NSSearchPathDirectory ns_directory;

    switch (type) {
      case GHOST_kUserSpecialDirDesktop:
        ns_directory = NSDesktopDirectory;
        break;
      case GHOST_kUserSpecialDirDocuments:
        ns_directory = NSDocumentDirectory;
        break;
      case GHOST_kUserSpecialDirDownloads:
        ns_directory = NSDownloadsDirectory;
        break;
      case GHOST_kUserSpecialDirMusic:
        ns_directory = NSMusicDirectory;
        break;
      case GHOST_kUserSpecialDirPictures:
        ns_directory = NSPicturesDirectory;
        break;
      case GHOST_kUserSpecialDirVideos:
        ns_directory = NSMoviesDirectory;
        break;
      case GHOST_kUserSpecialDirCaches:
        ns_directory = NSCachesDirectory;
        break;
      default:
        GHOST_ASSERT(
            false,
            "GHOST_SystemPathsCocoa::getUserSpecialDir(): Invalid enum value for type parameter");
        return NULL;
    }

    const NSArray *const paths = NSSearchPathForDirectoriesInDomains(
        ns_directory, NSUserDomainMask, YES);
    if ([paths count] == 0) {
      return NULL;
    }
    const NSString *const basePath = [paths objectAtIndex:0];

    strncpy(tempPath, [basePath cStringUsingEncoding:NSASCIIStringEncoding], sizeof(tempPath));
  }
  return tempPath;
}

const char *GHOST_SystemPathsCocoa::getBinaryDir() const
{
  static char tempPath[512] = "";

  @autoreleasepool {
    const NSString *const basePath = [[NSBundle mainBundle] bundlePath];

    if (basePath == nil) {
      return NULL;
    }

    strcpy(tempPath, [basePath cStringUsingEncoding:NSASCIIStringEncoding]);
  }
  return tempPath;
}

void GHOST_SystemPathsCocoa::addToSystemRecentFiles(const char *filename) const
{
  /* TODO: implement for macOS */
}