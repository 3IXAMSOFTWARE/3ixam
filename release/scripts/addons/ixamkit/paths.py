

import bpy, os, sys

_presets = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets")
IXAMKIT_LOCAL = "http://localhost:8001"
IXAMKIT_MAIN = "https://www.ixamkit.com"
IXAMKIT_DEVEL = "https://devel.ixamkit.com"
IXAMKIT_API = "/api/v1/"
IXAMKIT_REPORT_URL = "usage_report/"
IXAMKIT_USER_ASSETS = "/my-assets"
IXAMKIT_PLANS = "https://www.ixamkit.com/plans/pricing/"
IXAMKIT_MANUAL = "https://youtu.be/1hVgcQhIAo8"
IXAMKIT_MODEL_UPLOAD_INSTRUCTIONS_URL = "https://www.ixamkit.com/docs/upload/"
IXAMKIT_MATERIAL_UPLOAD_INSTRUCTIONS_URL = "https://www.ixamkit.com/docs/uploading-material/"
IXAMKIT_BRUSH_UPLOAD_INSTRUCTIONS_URL = "https://www.ixamkit.com/docs/uploading-brush/"
IXAMKIT_LOGIN_URL = "https://www.ixamkit.com/accounts/login"
IXAMKIT_OAUTH_LANDING_URL = "/oauth-landing/"
IXAMKIT_SIGNUP_URL = "https://www.ixamkit.com/accounts/register"
IXAMKIT_ADDON_URL = "https://www.ixamkit.com/api/v1/assets/6923b215-7df0-46f3-95ae-a2b5ff44ddd5/"
IXAMKIT_ADDON_FILE_URL = "https://www.ixamkit.com/get-ixamkit/"
IXAMKIT_SETTINGS_FILENAME = os.path.join(_presets, "bkit.json")


def get_bkit_url():
    # bpy.app.debug_value = 2
    d = bpy.app.debug_value
    # d = 2
    if d == 1:
        url = IXAMKIT_LOCAL
    elif d == 2:
        url = IXAMKIT_DEVEL
    else:
        url = IXAMKIT_MAIN
    return url

def find_in_local(text=''):
    fs = []
    for p, d, f in os.walk('.'):
        for file in f:
            if text in file:
                fs.append(file)
    return fs

def get_api_url():
    return get_bkit_url() + IXAMKIT_API

def get_oauth_landing_url():
    return get_bkit_url() + IXAMKIT_OAUTH_LANDING_URL


def default_global_dict():
    from os.path import expanduser
    home = expanduser("~")
    return home + os.sep + 'ixamkit_data'


def get_categories_filepath():
    tempdir = get_temp_dir()
    return os.path.join(tempdir, 'categories.json')


def get_temp_dir(subdir=None):
    user_preferences = bpy.context.preferences.addons['ixamkit'].preferences

    # tempdir = user_preferences.temp_dir
    tempdir = os.path.join(user_preferences.global_dir, 'temp')
    if tempdir.startswith('//'):
        tempdir = bpy.path.abspath(tempdir)
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    if subdir is not None:
        tempdir = tempdir + os.sep + subdir
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
    return tempdir


def get_download_dirs(asset_type):
    ''' get directories where assets will be downloaded'''
    subdmapping = {'brush': 'brushes', 'texture': 'textures', 'model': 'models', 'scene': 'scenes',
                   'material': 'materials'}

    user_preferences = bpy.context.preferences.addons['ixamkit'].preferences
    dirs = []
    if user_preferences.directory_behaviour == 'BOTH' or 'GLOBAL':
        ddir = user_preferences.global_dir
        if ddir.startswith('//'):
            ddir = bpy.path.abspath(ddir)
        if not os.path.exists(ddir):
            os.makedirs(ddir)

        subdirs = ['brushes', 'textures', 'models', 'scenes', 'materials']
        for subd in subdirs:
            subdir = ddir + os.sep + subd
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            if subdmapping[asset_type] == subd:
                dirs.append(subdir)
    if (
            user_preferences.directory_behaviour == 'BOTH' or user_preferences.directory_behaviour == 'LOCAL') and bpy.data.is_saved:  # it's important local get's solved as second, since for the linking process only last filename will be taken. For download process first name will be taken and if 2 filenames were returned, file will be copied to the 2nd path.
        ddir = user_preferences.project_subdir
        if ddir.startswith('//'):
            ddir = bpy.path.abspath(ddir)
            if not os.path.exists(ddir):
                os.makedirs(ddir)

        subdirs = ['textures', 'models', 'scenes', 'materials']  # brushes get stored only globally.
        for subd in subdirs:
            subdir = ddir + os.sep + subd
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            if subdmapping[asset_type] == subd:
                dirs.append(subdir)

    return dirs


def slugify(slug):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata, re
    slug = slug.lower()
    slug = slug.replace('.', '_')
    slug = slug.replace('"', '')
    slug = slug.replace(' ', '_')
    # import re
    # slug = unicodedata.normalize('NFKD', slug)
    # slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+.- ', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    slug = re.sub(r'/', '_', slug)
    return slug


def extract_filename_from_url(url):
    if url is not None:
        imgname = url.split('/')[-1]
        imgname = imgname.split('?')[0]
        return imgname
    return ''


def get_download_filenames(asset_data):
    dirs = get_download_dirs(asset_data['asset_type'])
    file_names = []
    # fn = asset_data['file_name'].replace('ixam_', '')
    if asset_data.get('url') is not None:
        # this means asset is already in scene and we don't need to check

        fn = extract_filename_from_url(asset_data['url'])
        fn.replace('_ixam', '')
        n = slugify(asset_data['name']) + '_' + fn
        # n = 'x.ixam'
        # strs = (n, asset_data['name'], asset_data['file_name'])
        for d in dirs:
            file_name = os.path.join(d, n)
            file_names.append(file_name)
    return file_names


def delete_asset_debug(asset_data):
    from ixamkit import download
    user_preferences = bpy.context.preferences.addons['ixamkit'].preferences
    api_key = user_preferences.api_key

    download.get_download_url(asset_data, download.get_scene_id(), api_key)

    file_names = get_download_filenames(asset_data)
    for f in file_names:
        if os.path.isfile(f):
            try:
                print(f)
                os.remove(f)
            except:
                e = sys.exc_info()[0]
                print(e)
                pass;


def get_clean_filepath():
    script_path = os.path.dirname(os.path.realpath(__file__))
    subpath = "ixamfiles" + os.sep + "cleaned.ixam"
    cp = os.path.join(script_path, subpath)
    return cp


def get_thumbnailer_filepath():
    script_path = os.path.dirname(os.path.realpath(__file__))
    # fpath = os.path.join(p, subpath)
    subpath = "ixamfiles" + os.sep + "thumbnailer.ixam"
    return os.path.join(script_path, subpath)


def get_material_thumbnailer_filepath():
    script_path = os.path.dirname(os.path.realpath(__file__))
    # fpath = os.path.join(p, subpath)
    subpath = "ixamfiles" + os.sep + "material_thumbnailer_cycles.ixam"
    return os.path.join(script_path, subpath)
    """
    for p in bpy.utils.script_paths():
        testfname= os.path.join(p, subpath)#p + '%saddons%sobject_fracture%sdata.ixam' % (s,s,s)
        if os.path.isfile( testfname):
            fname=testfname
            return(fname)
    return None
    """


def get_addon_file(subpath=''):
    script_path = os.path.dirname(os.path.realpath(__file__))
    # fpath = os.path.join(p, subpath)
    return os.path.join(script_path, subpath)


def get_addon_thumbnail_path(name):
    script_path = os.path.dirname(os.path.realpath(__file__))
    # fpath = os.path.join(p, subpath)
    ext = name.split('.')[-1]
    next = ''
    if not (ext == 'jpg' or ext == 'png'):  # already has ext?
        next = '.jpg'
    subpath = "thumbnails" + os.sep + name + next
    return os.path.join(script_path, subpath)
