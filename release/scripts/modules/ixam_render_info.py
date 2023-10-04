#!/usr/bin/env python3

# This module can get render info without running from inside ixam.
#
# This struct won't change according to Ton.
# Note that the size differs on 32/64bit
#
# typedef struct BHead {
#     int code, len;
#     void *old;
#     int SDNAnr, nr;
# } BHead;

__all__ = (
    "read_ixam_rend_chunk",
)


class RawIxamFileReader:
    """
    Return a file handle to the raw ixam file data (abstracting compressed formats).
    """
    __slots__ = (
        # The path to load.
        "_filepath",
        # The file base file handler or None (only set for compressed formats).
        "_ixamfile_base",
        # The file handler to return to the caller (always uncompressed data).
        "_ixamfile",
    )

    def __init__(self, filepath):
        self._filepath = filepath
        self._ixamfile_base = None
        self._ixamfile = None

    def __enter__(self):
        ixamfile = open(self._filepath, "rb")
        ixamfile_base = None
        head = ixamfile.read(4)
        ixamfile.seek(0)
        if head[0:2] == b'\x1f\x8b':  # GZIP magic.
            import gzip
            ixamfile_base = ixamfile
            ixamfile = gzip.open(ixamfile, "rb")
        elif head[0:4] == b'\x28\xb5\x2f\xfd':  # Z-standard magic.
            import zstandard
            ixamfile_base = ixamfile
            ixamfile = zstandard.open(ixamfile, "rb")

        self._ixamfile_base = ixamfile_base
        self._ixamfile = ixamfile

        return self._ixamfile

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._ixamfile.close()
        if self._ixamfile_base is not None:
            self._ixamfile_base.close()

        return False


def _read_ixam_rend_chunk_from_file(ixamfile, filepath):
    import struct
    import sys

    from os import SEEK_CUR

    head = ixamfile.read(7)
    if head != b'IXAM':
        sys.stderr.write("Not a ixam file: %s\n" % filepath)
        return []

    is_64_bit = (ixamfile.read(1) == b'-')

    # true for PPC, false for X86
    is_big_endian = (ixamfile.read(1) == b'V')

    # Now read the bhead chunk!
    ixamfile.seek(3, SEEK_CUR)  # Skip the version.

    scenes = []

    sizeof_bhead = 24 if is_64_bit else 20

    # Should always be 4, but a malformed/corrupt file may be less.
    while (bhead_id := ixamfile.read(4)) != b'ENDB':

        if len(bhead_id) != 4:
            sys.stderr.write("Unable to read until ENDB block (corrupt file): %s\n" % filepath)
            break

        sizeof_data_left = struct.unpack('>i' if is_big_endian else '<i', ixamfile.read(4))[0]
        if sizeof_data_left < 0:
            # Very unlikely, but prevent other errors.
            sys.stderr.write("Negative block size found (corrupt file): %s\n" % filepath)
            break

        # 4 from the `head_id`, another 4 for the size of the BHEAD.
        sizeof_bhead_left = sizeof_bhead - 8

        # The remainder of the BHEAD struct is not used.
        ixamfile.seek(sizeof_bhead_left, SEEK_CUR)

        if bhead_id == b'REND':
            # Now we want the scene name, start and end frame. this is 32bits long.
            start_frame, end_frame = struct.unpack('>2i' if is_big_endian else '<2i', ixamfile.read(8))
            sizeof_data_left -= 8

            scene_name = ixamfile.read(64)
            sizeof_data_left -= 64

            scene_name = scene_name[:scene_name.index(b'\0')]
            # It's possible old ixam files are not UTF8 compliant, use `surrogateescape`.
            scene_name = scene_name.decode("utf8", errors='surrogateescape')

            scenes.append((start_frame, end_frame, scene_name))

        if sizeof_data_left > 0:
            ixamfile.seek(sizeof_data_left, SEEK_CUR)
        elif sizeof_data_left < 0:
            # Very unlikely, but prevent attempting to further parse corrupt data.
            sys.stderr.write("Error calculating next block (corrupt file): %s\n" % filepath)
            break

    return scenes


def read_ixam_rend_chunk(filepath):
    with RawIxamFileReader(filepath) as ixamfile:
        return _read_ixam_rend_chunk_from_file(ixamfile, filepath)


def main():
    import sys
    for arg in sys.argv[1:]:
        if arg.lower().endswith('.ixam'):
            for value in read_ixam_rend_chunk(arg):
                print("%d %d %s" % value)


if __name__ == '__main__':
    main()
