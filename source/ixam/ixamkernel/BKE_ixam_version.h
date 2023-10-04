#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/** \file
 * \ingroup bke
 */

/**
 * The lines below use regex from scripts to extract their values,
 * Keep this in mind when modifying this file and keep this comment above the defines.
 *
 * \note Use #STRINGIFY() rather than defining with quotes.
 */

/* 3IXAM major and minor version. */
#define IXAM_VERSION 130
/* 3IXAM patch version for bugfix releases. */
#define IXAM_VERSION_PATCH 2
/** 3IXAM release cycle stage: alpha/beta/rc/release. */
#define IXAM_VERSION_CYCLE release

/* 3IXAM file format version. */
#define IXAM_FILE_VERSION IXAM_VERSION
#define IXAM_FILE_SUBVERSION 6

/* Minimum 3IXAM version that supports reading file written with the current
 * version. Older 3IXAM versions will test this and show a warning if the file
 * was written with too new a version. */
#define IXAM_FILE_MIN_VERSION 2
#define IXAM_FILE_MIN_SUBVERSION 0

/** User readable version string. */
const char *BKE_ixam_version_string(void);

/* Returns true when version cycle is alpha, otherwise (beta, rc) returns false. */
bool BKE_ixam_version_is_alpha(void);

#ifdef __cplusplus
}
#endif
