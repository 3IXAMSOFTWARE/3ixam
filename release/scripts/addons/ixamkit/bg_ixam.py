

if "bpy" in locals():
    from importlib import reload

    utils = reload(utils)
else:
    from ixamkit import utils

import bpy
import sys, threading, os
import re

from bpy.props import (
    EnumProperty,
)

bg_processes = []


class threadCom:  # object passed to threads to read background process stdout info
    ''' Object to pass data between thread and '''

    def __init__(self, eval_path_computing, eval_path_state, eval_path, process_type, proc, location=None, name=''):
        # self.obname=ob.name
        self.name = name
        self.eval_path_computing = eval_path_computing  # property that gets written to.
        self.eval_path_state = eval_path_state  # property that gets written to.
        self.eval_path = eval_path  # property that gets written to.
        self.process_type = process_type
        self.outtext = ''
        self.proc = proc
        self.lasttext = ''
        self.message = ''  # the message to be sent.
        self.progress = 0.0
        self.location = location
        self.error = False
        self.log = ''


def threadread(tcom):
    '''reads stdout of background process, done this way to have it non-blocking. this threads basically waits for a stdout line to come in, fills the data, dies.'''
    found = False
    while not found:
        inline = tcom.proc.stdout.readline()
        # print('readthread', time.time())
        inline = str(inline)
        s = inline.find('progress{')
        if s > -1:
            e = inline.find('}')
            tcom.outtext = inline[s + 9:e]
            found = True
            if tcom.outtext.find('%') > -1:
                tcom.progress = float(re.findall('\d+\.\d+|\d+', tcom.outtext)[0])
            return
        if s == -1:
            s = inline.find('Remaining')
            if s > -1:
                # e=inline.find('}')
                tcom.outtext = inline[s: s + 18]
                found = True
                return
        if len(inline) > 3:
            print(inline, len(inline))
        # if inline.find('Error'):
        #    tcom.error = True
        #     tcom.outtext = inline[2:]


def progress(text, n=None):
    '''function for reporting during the script, works for background operations in the header.'''
    # for i in range(n+1):
    # sys.stdout.flush()
    text = str(text)
    if n is None:
        n = ''
    else:
        n = ' ' + ' ' + str(int(n * 1000) / 1000) + '% '
    spaces = ' ' * (len(text) + 55)
    sys.stdout.write('progress{%s%s}\n' % (text, n))
    sys.stdout.flush()


@bpy.app.handlers.persistent
def bg_update():
    '''monitoring of background process'''
    text = ''
    s = bpy.context.scene

    global bg_processes
    if len(bg_processes) == 0:
        return 2

    for p in bg_processes:
        # proc=p[1].proc
        readthread = p[0]
        tcom = p[1]
        if not readthread.is_alive():
            readthread.join()
            # readthread.
            if tcom.error:
                estring = tcom.eval_path_computing + ' = False'
                exec(estring)

            tcom.lasttext = tcom.outtext
            if tcom.outtext != '':
                tcom.outtext = ''
                estring = tcom.eval_path_state + ' = tcom.lasttext'

                exec(estring)
            # print(tcom.lasttext)
            if 'finished successfully' in tcom.lasttext:
                bg_processes.remove(p)
                estring = tcom.eval_path_computing + ' = False'
                exec(estring)
            else:
                readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
                readthread.start()
                p[0] = readthread
    # if len(bg_processes) == 0:
    #     bpy.app.timers.unregister(bg_update)
    if len(bg_processes) > 0:
        return .3
    return 1.


process_types = (
    ('UPLOAD', 'Upload', ''),
    ('THUMBNAILER', 'Thumbnailer', ''),
)

process_sources = (
    ('MODEL', 'Model', 'set of objects'),
    ('SCENE', 'Scene', 'set of scenes'),
    ('MATERIAL', 'Material', 'any .ixam Material'),
    ('TEXTURE', 'Texture', 'a texture, or texture set'),
    ('BRUSH', 'Brush', 'brush, can be any type of 3IXAM brush'),
)


class KillBgProcess(bpy.types.Operator):
    '''Remove  processes in background.'''
    bl_idname = "object.kill_bg_process"
    bl_label = "Kill Background Process"
    bl_options = {'REGISTER'}

    process_type: EnumProperty(
        name="Type",
        items=process_types,
        description="Type of process",
        default="UPLOAD",
    )

    process_source: EnumProperty(
        name="Source",
        items=process_sources,
        description="Source of process",
        default="MODEL",
    )

    def execute(self, context):
        s = bpy.context.scene

        cls = bpy.ops.object.convert.__class__
        # first do the easy stuff...TODO all cases.
        props = utils.get_upload_props()
        if self.process_type == 'UPLOAD':
            props.uploading = False
        if self.process_type == 'THUMBNAILER':
            props.is_generating_thumbnail = False
        global ixamkit_bg_process
        # print('killing', self.process_source, self.process_type)
        # then go kill the process. this wasn't working for unsetting props and that was the reason for changing to the method above.

        processes = bg_processes
        for p in processes:

            tcom = p[1]
            # print(tcom.process_type, self.process_type)
            if tcom.process_type == self.process_type:
                source = eval(tcom.eval_path)
                print(source.bl_rna.name, self.process_source)
                print(source.name)
                kill = False
                if source.bl_rna.name == 'Object' and self.process_source == 'MODEL':
                    if source.name == bpy.context.active_object.name:
                        kill = True
                if source.bl_rna.name == 'Material' and self.process_source == 'MATERIAL':
                    if source.name == bpy.context.active_object.active_material.name:
                        kill = True
                if source.bl_rna.name == 'Brush' and self.process_source == 'BRUSH':
                    brush = utils.get_active_brush()
                    if brush is not None and source.name == brush.name:
                        kill = True
                if kill:
                    estring = tcom.eval_path_computing + ' = False'
                    exec(estring)
                    processes.remove(p)
                    tcom.proc.kill()

        return {'FINISHED'}


def add_bg_process(location=None, name=None, eval_path_computing='', eval_path_state='', eval_path='', process_type='',
                   process=None):
    '''adds process for monitoring'''
    global bg_processes
    tcom = threadCom(eval_path_computing, eval_path_state, eval_path, process_type, process, location, name)
    readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
    readthread.start()

    bg_processes.append([readthread, tcom])
    # if not bpy.app.timers.is_registered(bg_update):
    #     bpy.app.timers.register(bg_update, persistent=True)


def register():
    bpy.utils.register_class(KillBgProcess)
    bpy.app.timers.register(bg_update, persistent=True)


def unregister():
    bpy.utils.unregister_class(KillBgProcess)
    bpy.app.timers.unregister(bg_update)
