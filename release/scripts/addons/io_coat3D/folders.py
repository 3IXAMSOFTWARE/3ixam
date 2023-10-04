# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
import os

def InitFolders():

    platform = os.sys.platform
    coat3D = bpy.context.scene.coat3D

    #    Global variable foundExchangeFolder (True / False) guides these steps
    # 1. Read Exchange_folder.txt, if not success ->
    # 2. Try to find exchange folder from system hard drive, if not success -->
    # 3. Leave foundExchangeFolder = False

    # 1. #################################################################

    if(platform == 'win32' or platform == 'darwin'):
        DC2Folder = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Ixam'
    else:
        DC2Folder = os.path.expanduser("~") + os.sep + '3DC2Ixam'

    exchangeFile = DC2Folder + os.sep + 'Exchange_folder.txt'

    if(not os.path.isdir(DC2Folder)):
        os.mkdir(DC2Folder)

    if(not os.path.isfile(exchangeFile)):
        file = open(exchangeFile, 'w')
        file.close()
    else:
        savedExchangePath = ''
        folderPath = open(exchangeFile)

        for line in folderPath:
            savedExchangePath = line
            break
        folderPath.close()


        coat3D.exchangeFolder = savedExchangePath
        return True, coat3D.exchangeFolder


    # 2. #################################################################

    if(platform == 'win32' or platform == 'darwin'):
        exchangeFolder = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + 'Applinks' + os.sep + '3D-Coat' + os.sep +'Exchange'
    else:
        exchangeFolder = os.path.expanduser("~") + os.sep + '3D-CoatV4' + os.sep + 'Exchange'
        if not(os.path.isdir(exchangeFolder)):
            exchangeFolder = os.path.expanduser("~") + os.sep + '3D-CoatV3' + os.sep + 'Exchange'
    if(os.path.isdir(exchangeFolder)):
        coat3D.exchangeFolder = exchangeFolder

        Ixam_folder = ("%s%sIxam"%(exchangeFolder,os.sep))

        if(not(os.path.isdir(Ixam_folder))):
            os.makedirs(Ixam_folder, mode = 0o666)
            Ixam_folder1 = os.path.join(Ixam_folder,"run.txt")
            file = open(Ixam_folder1, "w")
            file.close()

            Ixam_folder2 = os.path.join(Ixam_folder, "extension.txt")
            file = open(Ixam_folder2, "w")
            file.write("fbx")
            file.close()

            Ixam_folder3 = os.path.join(Ixam_folder, "preset.txt")
            file = open(Ixam_folder3, "w")
            file.write("Ixam Cycles")
            file.close()

        file = open(exchangeFile, "w")
        file.write("%s"%(os.path.abspath(coat3D.exchangeFolder)))
        file.close()

        return True, coat3D.exchangeFolder

    return False, ''


def updateExchangeFile(newPath):

    platform = os.sys.platform

    if(platform == 'win32' or platform == 'darwin'):
        exchangeFile = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Ixam' + os.sep + 'Exchange_folder.txt'
    else:
        exchangeFile = os.path.expanduser("~") + os.sep + '3DC2Ixam' + os.sep + 'Exchange_folder.txt'
    if(os.path.isfile(exchangeFile)):
        folderPath = ''

    if(os.path.isfile(exchangeFile)):
        file = open(exchangeFile, "w")
        file.write("%s"%(newPath))
        file.close()

def loadExchangeFolder():

    platform = os.sys.platform
    coat3D = bpy.context.scene.coat3D

    if(platform == 'win32' or platform == 'darwin'):
        DC2Folder = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Ixam'
    else:
        DC2Folder = os.path.expanduser("~") + os.sep + '3DC2Ixam'

    exchangeFile = DC2Folder + os.sep + 'Exchange_folder.txt'

    if(not os.path.isdir(DC2Folder)):
        os.mkdir(DC2Folder)

    if(not os.path.isfile(exchangeFile)):
        file = open(exchangeFile, 'w')
        file.close()
    else:
        savedExchangePath = ''
        folderPath = open(exchangeFile)

        for line in folderPath:
            savedExchangePath = line
            break
        folderPath.close()
        coat3D.exchangeFolder = savedExchangePath


def set_working_folders():

    platform = os.sys.platform
    coat3D = bpy.context.scene.coat3D

    if(platform == 'win32' or platform == 'darwin'):
        if (coat3D.defaultfolder != '' and os.path.isdir(coat3D.defaultfolder)):
            return coat3D.defaultfolder
        else:
            folder_objects = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Ixam' + os.sep + 'ApplinkObjects'
            if(not(os.path.isdir(folder_objects))):
                os.makedirs(folder_objects, mode = 0o666)
    else:
        if (coat3D.defaultfolder != '' and os.path.isdir(coat3D.defaultfolder)):
            return coat3D.defaultfolder
        else:
            folder_objects = os.path.expanduser("~") + os.sep + '3DC2Ixam' + os.sep + 'ApplinkObjects'
            if(not(os.path.isdir(folder_objects))):
                os.makedirs(folder_objects, mode = 0o666)

    return folder_objects
