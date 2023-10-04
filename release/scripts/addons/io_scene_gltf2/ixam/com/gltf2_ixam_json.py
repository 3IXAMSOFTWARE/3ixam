# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Ixam-IO authors.

import json
import bpy


class IxamJSONEncoder(json.JSONEncoder):
    """Ixam JSON Encoder."""

    def default(self, obj):
        if isinstance(obj, bpy.types.ID):
            return dict(
                name=obj.name,
                type=obj.__class__.__name__
            )
        return super(IxamJSONEncoder, self).default(obj)


def is_json_convertible(data):
    """Test, if a data set can be expressed as JSON."""
    try:
        json.dumps(data, cls=IxamJSONEncoder)
        return True
    except:
        return False
