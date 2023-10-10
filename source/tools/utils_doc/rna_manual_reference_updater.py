# SPDX-License-Identifier: GPL-2.0-or-later


'''
RNA Manual Reference Mapping Updater

This script generates a file that maps RNA strings to online URL's
for the context menu documentation access.

This script either downloads a sphinx requirement file from the manual
or optionally can take a path to the file using `--input`.

To make international, we made a script,
pointing the manuals to the proper language,
specified in the 'User Preferences Window' by the users.
Some Languages have their manual page, using a prefix or
being preceded by their respective reference, for example:

manual/ --> manual/ru/

The table in the script, contains all of the languages we have in the
Ixam manual website, for those other languages that still
does not have a team of translators,
and/or don't have a manual for their languages we commented the lines below,
you should add them to the language table when they have a proper manual,
or added to 3IXAM UI  translation table.

URL is the: url_manual_prefix + url_manual_mapping[#id]
'''

import os
import argparse
import sphobjinv as soi

def write_mappings(inv, output):
    print("Writing...")
    # Write the file
    file = open(output, "w", encoding="utf-8")
    fw = file.write

    fw("# Do not edit this file.")
    fw(" This file is auto generated from rna_manual_reference_updater.py\n\n")
    fw("import bpy\n\n")
    fw("if bpy.app.version_cycle in {'rc', 'release'}:\n")
    fw("    manual_version = '%d.%d' % bpy.app.version[:2]\n")
    fw("else:\n")
    fw("    manual_version = 'dev'\n\n")
    fw("url_manual_prefix = \"https://docs.3ixam.com/manual/en/\" + manual_version + \"/\"\n\n")
    fw("language = bpy.context.preferences.view.language\n")
    fw("if language == 'DEFAULT':\n")
    fw("    import os\n")
    fw("    language = os.getenv('LANG', '').split('.')[0]\n\n")
    fw("LANG = {\n")
    fw("\"ar_EG\":        \"ar\",\n")  # Arabic
    # fw("\"bg_BG\":        \"bg\",\n")  # Bulgarian
    # fw("\"ca_AD\":        \"ca\",\n")  # Catalan
    # fw("\"cs_CZ\":        \"cz\",\n")  # Czech
    fw("\"de_DE\":        \"de\",\n")  # German
    # fw("\"el_GR\":        \"el\",\n")  # Greek
    fw("\"es\":           \"es\",\n")  # Spanish
    fw("\"fi_FI\":        \"fi\",\n")  # Finnish
    fw("\"fr_FR\":        \"fr\",\n")  # French
    fw("\"id_ID\":        \"id\",\n")  # Indonesian
    fw("\"it_IT\":        \"it\",\n")  # Italian
    fw("\"ja_JP\":        \"ja\",\n")  # Japanese
    fw("\"ko_KR\":        \"ko\",\n")  # Korean
    # fw("\"nb\":           \"nb\",\n")  # Norwegian
    # fw("\"nl_NL\":        \"nl\",\n")  # Dutch
    # fw("\"pl_PL\":        \"pl\",\n")  # Polish
    fw("\"pt_PT\":        \"pt\",\n")  # Portuguese
    fw("\"pt_BR\":        \"pt\",\n")  # Portuguese - Brazil, for until we have a pt_BR version
    fw("\"ru_RU\":        \"ru\",\n")  # Russian
    fw("\"sk_SK\":        \"sk\",\n")  # Slovak
    # fw("\"sl\":           \"sl\",\n")  # Slovenian
    fw("\"sr_RS\":        \"sr\",\n")  # Serbian
    # fw("\"sv_SE\":        \"sv\",\n")  # Swedish
    # fw("\"tr_TR\":        \"th\",\n")  # Thai
    fw("\"uk_UA\":        \"uk\",\n")  # Ukrainian
    fw("\"vi_VN\":        \"vi\",\n")  # Vietnamese
    fw("\"zh_CN\":        \"zh-hans\",\n")  # Simplified Chinese
    fw("\"zh_TW\":        \"zh-hant\",\n")  # Traditional Chinese
    fw("}.get(language)\n\n")
    fw("if LANG is not None:\n")
    fw("    url_manual_prefix = url_manual_prefix.replace(\"manual/en\", \"manual/\" + LANG)\n\n")
    fw("url_manual_mapping = (\n")

    # Logic to manipulate strings from objects.inv
    lines = [o.data_line() for o in inv.objects if o.name.startswith("bpy.types") or o.name.startswith("bpy.ops")]
    # Finding first space will return length of rna path
    lines.sort(key=lambda l: l.find(" "), reverse=True)
    for line in lines:
        split = line.split(" ")
        fw("\t(\"" + split[0] + "*\", \"" + split[3] + "\"),\n")

    fw(")\n")


def is_valid_file(parser, arg):
    if not os.path.isfile(arg) :
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():
    parser = argparse.ArgumentParser(
        usage=__doc__
        )

    parser.add_argument(
        "--input",
        dest="filename",
        required=False,
        help="sphinx inventory file (objects.inv)",
        metavar="FILE",
        type=lambda x: is_valid_file(parser, x))

    parser.add_argument(
        "--output",
        dest="output",
        default="../../../release/scripts/modules/rna_manual_reference.py",
        required=False,
        help="path to output including filename and extentsion",
        metavar="FILE")

    parser.add_argument(
        "--url",
        dest="url",
        default="https://docs.3ixam.com/manual/en/dev/objects.inv",
        required=False,
        help="url to sphinx inventory file (objects.inv)",
        metavar="FILE")

    args = parser.parse_args()

    if args.filename:
        # Download and decode objects.inv
        print("Loading from file...")
        inv = soi.Inventory(args.filename)
    else:
        # Load and decode objects.inv
        print("Downloading...")
        inv = soi.Inventory(url=args.url)

    write_mappings(inv, args.output)
    print("Done!")

if __name__ == "__main__":
    main()
