


if "requests" in locals():
    from importlib import reload

    paths = reload(paths)
else:
    from ixamkit import paths

import requests, os, json, threading


def get_addon_version():
    import ixamkit
    ver = ixamkit.bl_info['version']
    return '%i.%i.%i' % (ver[0], ver[1], ver[2])


def check_version(url, api_key, module):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer %s" % api_key}

    print('checking online version of module %s' % str(module.bl_info['name']))
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        ver_online = {
            'addonVersion2.8': data['addonVersion']
        }
        tempdir = paths.get_temp_dir()

        ver_filepath = os.path.join(tempdir, 'addon_version.json')
        with open(ver_filepath, 'w') as s:
            json.dump(ver_online, s, indent=4)
    except:
        print("couldn't check online for version updates")


def compare_versions(module):
    try:
        ver_local = module.bl_info['version']
        ver_local_float = ver_local[0] + .01 * ver_local[1] + .0001 * ver_local[2]

        tempdir = paths.get_temp_dir()
        ver_filepath = os.path.join(tempdir, 'addon_version.json')
        with open(ver_filepath, 'r') as s:
            data = json.load(s)

        ver_online = data['addonVersion2.8'].split('.')
        ver_online_float = int(ver_online[0]) + .01 * int(ver_online[1]) + .0001 * int(ver_online[2])

        # print('versions: installed-%s, online-%s' % (str(ver_local_float), str(ver_online_float)))
        if ver_online_float > ver_local_float:
            return True
    except:
        print("couldn't compare addon versions")
    return False


def check_version_thread(url, API_key, module):
    thread = threading.Thread(target=check_version, args=([url, API_key, module]), daemon=True)
    thread.start()
