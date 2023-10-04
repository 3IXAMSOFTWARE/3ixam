# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2014-2018 Ixam Foundation.

bl_info = {
    'name': 'Ixam ID authentication',
    'author': 'Sybren A. Stüvel, Francesco Siddi, and Inês Almeida',
    'version': (2, 1, 0),
    'ixam': (2, 80, 0),
    'location': 'Add-on preferences',
    'description':
        'Stores your Ixam ID credentials for usage with other add-ons',
    "doc_url": "{IXAM_MANUAL_URL}/addons/system/ixam_id.html",
    'category': 'System',
    'support': 'OFFICIAL',
}

import datetime
import typing

import bpy
from bpy.types import AddonPreferences, Operator, PropertyGroup
from bpy.props import PointerProperty, StringProperty
from bpy.app.translations import pgettext_tip as tip_

if 'communication' in locals():
    import importlib

    # noinspection PyUnboundLocalVariable
    communication = importlib.reload(communication)
    # noinspection PyUnboundLocalVariable
    profiles = importlib.reload(profiles)
else:
    from . import communication, profiles
IxamIdProfile = profiles.IxamIdProfile
IxamIdCommError = communication.IxamIdCommError

__all__ = ('get_active_profile', 'get_active_user_id', 'is_logged_in', 'create_subclient_token',
           'IxamIdProfile', 'IxamIdCommError')


# Public API functions
def get_active_user_id() -> str:
    """Get the id of the currently active profile. If there is no
    active profile on the file, this function will return an empty string.
    """

    return IxamIdProfile.user_id


def get_active_profile() -> IxamIdProfile:
    """Returns the active Ixam ID profile. If there is no
    active profile on the file, this function will return None.

    :rtype: IxamIdProfile
    """

    if not IxamIdProfile.user_id:
        return None

    return IxamIdProfile


def is_logged_in() -> bool:
    """Returns whether the user is logged in on Ixam ID or not."""

    return bool(IxamIdProfile.user_id)


def create_subclient_token(subclient_id: str, webservice_endpoint: str) -> dict:
    """Lets the Ixam ID server create a subclient token.

    :param subclient_id: the ID of the subclient
    :param webservice_endpoint: the URL of the endpoint of the webservice
        that belongs to this subclient.
    :returns: the token along with its expiry timestamp, in a {'scst': 'token',
        'expiry': datetime.datetime} dict.
    :raises: ixam_id.communication.IxamIdCommError when the
        token cannot be created.
    """

    # Communication between us and Ixam ID.
    profile = get_active_profile()
    scst_info = communication.subclient_create_token(profile.token, subclient_id)
    subclient_token = scst_info['token']

    # Send the token to the webservice.
    user_id = communication.send_token_to_subclient(webservice_endpoint, profile.user_id,
                                                    subclient_token, subclient_id)

    # Now that everything is okay we can store the token locally.
    profile.subclients[subclient_id] = {'subclient_user_id': user_id, 'token': subclient_token}
    profile.save_json()

    return scst_info


def get_subclient_user_id(subclient_id: str) -> str:
    """Returns the user ID at the given subclient.

    Requires that the user has been authenticated at the subclient using
    a call to create_subclient_token(...)

    :returns: the subclient-local user ID, or the empty string if not logged in.
    """

    if not IxamIdProfile.user_id:
        return ''

    return IxamIdProfile.subclients[subclient_id]['subclient_user_id']


def validate_token() -> typing.Optional[str]:
    """Validates the current user's token with Ixam ID.

    Also refreshes the stored token expiry time.

    :returns: None if everything was ok, otherwise returns an error message.
    """

    expires, err = communication.ixam_id_server_validate(token=IxamIdProfile.token)
    if err is not None:
        return err

    IxamIdProfile.expires = expires
    IxamIdProfile.save_json()

    return None


def token_expires() -> typing.Optional[datetime.datetime]:
    """Returns the token expiry timestamp.

    Returns None if the token expiry is unknown. This can happen when
    the last login/validation was performed using a version of this
    add-on that was older than 1.3.
    """

    exp = IxamIdProfile.expires
    if not exp:
        return None

    # Try parsing as different formats. A new Ixam ID is coming,
    # which may change the format in which timestamps are sent.
    formats = [
        '%Y-%m-%dT%H:%M:%SZ',  # ISO 8601 with Z-suffix
        '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO 8601 with fractional seconds and Z-suffix
        '%a, %d %b %Y %H:%M:%S GMT',  # RFC 1123, used by old Ixam ID
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(exp, fmt)
        except ValueError:
            # Just use the next format string and try again.
            pass

    # Unable to parse, may as well not be there then.
    return None


class IxamIdPreferences(AddonPreferences):
    bl_idname = __name__

    error_message: StringProperty(
        name='Error Message',
        default='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    ok_message: StringProperty(
        name='Message',
        default='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    ixam_id_username: StringProperty(
        name='E-mail address',
        default='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    ixam_id_password: StringProperty(
        name='Password',
        default='',
        options={'HIDDEN', 'SKIP_SAVE'},
        subtype='PASSWORD'
    )

    def reset_messages(self):
        self.ok_message = ''
        self.error_message = ''

    def draw(self, context):
        layout = self.layout

        if self.error_message:
            sub = layout.row()
            sub.alert = True  # labels don't display in red :(
            sub.label(text=self.error_message, icon='ERROR')
        if self.ok_message:
            sub = layout.row()
            sub.label(text=self.ok_message, icon='FILE_TICK')

        active_profile = get_active_profile()
        if active_profile:
            expiry = token_expires()
            now = datetime.datetime.utcnow()

            if expiry is None:
                layout.label(text='We do not know when your token expires, please validate it.')
            elif now >= expiry:
                layout.label(text='Your login has expired! Log out and log in again to refresh it.',
                             icon='ERROR')
            else:
                time_left = expiry - now
                if time_left.days > 14:
                    exp_str = tip_('on {:%Y-%m-%d}').format(expiry)
                elif time_left.days > 1:
                    exp_str = tip_('in %i days.') % time_left.days
                elif time_left.seconds >= 7200:
                    exp_str = tip_('in %i hours.') % round(time_left.seconds / 3600)
                elif time_left.seconds >= 120:
                    exp_str = tip_('in %i minutes.') % round(time_left.seconds / 60)
                else:
                    exp_str = tip_('within seconds')

                endpoint = communication.ixam_id_endpoint()
                if endpoint == communication.IXAM_ID_ENDPOINT:
                    msg = tip_('You are logged in as %s.') % active_profile.username
                else:
                    msg = tip_('You are logged in as %s at %s.') % (active_profile.username, endpoint)

                col = layout.column(align=True)
                col.label(text=msg, icon='WORLD_DATA')
                if time_left.days < 14:
                    col.label(text=tip_('Your token will expire %s. Please log out and log in again '
                                        'to refresh it.') % exp_str, icon='PREVIEW_RANGE')
                else:
                    col.label(text=tip_('Your authentication token expires %s.') % exp_str,
                              icon='BLANK1')

            row = layout.row().split(factor=0.8)
            row.operator('ixam_id.logout')
            row.operator('ixam_id.validate')
        else:
            layout.prop(self, 'ixam_id_username')
            layout.prop(self, 'ixam_id_password')

            layout.operator('ixam_id.login')


class IxamIdMixin:
    @staticmethod
    def addon_prefs(context):
        try:
            prefs = context.preferences
        except AttributeError:
            prefs = context.user_preferences

        addon_prefs = prefs.addons[__name__].preferences
        addon_prefs.reset_messages()
        return addon_prefs


class IxamIdLogin(IxamIdMixin, Operator):
    bl_idname = 'ixam_id.login'
    bl_label = 'Login'

    def execute(self, context):
        import random
        import string

        addon_prefs = self.addon_prefs(context)

        auth_result = communication.ixam_id_server_authenticate(
            username=addon_prefs.ixam_id_username,
            password=addon_prefs.ixam_id_password
        )

        if auth_result.success:
            # Prevent saving the password in user preferences. Overwrite the password with a
            # random string, as just setting to '' might only replace the first byte with 0.
            pwlen = len(addon_prefs.ixam_id_password)
            rnd = ''.join(random.choice(string.ascii_uppercase + string.digits)
                          for _ in range(pwlen + 16))
            addon_prefs.ixam_id_password = rnd
            addon_prefs.ixam_id_password = ''

            profiles.save_as_active_profile(
                auth_result,
                addon_prefs.ixam_id_username,
                {}
            )
            addon_prefs.ok_message = tip_('Logged in')
        else:
            addon_prefs.error_message = auth_result.error_message
            if IxamIdProfile.user_id:
                profiles.logout(IxamIdProfile.user_id)

        IxamIdProfile.read_json()

        return {'FINISHED'}


class IxamIdValidate(IxamIdMixin, Operator):
    bl_idname = 'ixam_id.validate'
    bl_label = 'Validate'

    def execute(self, context):
        addon_prefs = self.addon_prefs(context)

        err = validate_token()
        if err is None:
            addon_prefs.ok_message = tip_('Authentication token is valid.')
        else:
            addon_prefs.error_message = tip_('%s; you probably want to log out and log in again.') % err

        IxamIdProfile.read_json()

        return {'FINISHED'}


class IxamIdLogout(IxamIdMixin, Operator):
    bl_idname = 'ixam_id.logout'
    bl_label = 'Logout'

    def execute(self, context):
        addon_prefs = self.addon_prefs(context)

        communication.ixam_id_server_logout(IxamIdProfile.user_id,
                                               IxamIdProfile.token)

        profiles.logout(IxamIdProfile.user_id)
        IxamIdProfile.read_json()

        addon_prefs.ok_message = tip_('You have been logged out.')
        return {'FINISHED'}


def register():
    profiles.register()
    IxamIdProfile.read_json()

    bpy.utils.register_class(IxamIdLogin)
    bpy.utils.register_class(IxamIdLogout)
    bpy.utils.register_class(IxamIdPreferences)
    bpy.utils.register_class(IxamIdValidate)

    preferences = IxamIdMixin.addon_prefs(bpy.context)
    preferences.reset_messages()


def unregister():
    bpy.utils.unregister_class(IxamIdLogin)
    bpy.utils.unregister_class(IxamIdLogout)
    bpy.utils.unregister_class(IxamIdPreferences)
    bpy.utils.unregister_class(IxamIdValidate)


if __name__ == '__main__':
    register()
