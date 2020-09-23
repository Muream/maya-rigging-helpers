# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.cmds as cmds
from mrh.plugins import angle_helper
import mrh.plugins.angle_helper as angle_helper
import mrh.plugins.angle_cone_helper as angle_cone_helper
import mrh.plugins.vector_helper as vector_helper

reload(angle_helper)
reload(angle_cone_helper)
reload(vector_helper)

logger = logging.getLogger(__name__)


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


def initializePlugin(plugin):
    vendor = "Loic Pinsard"
    version = "1.0.0"
    api_version = "Any"

    plugin_fn = om.MFnPlugin(plugin, vendor, version, api_version)
    angle_helper.register(plugin_fn)
    angle_cone_helper.register(plugin_fn)
    vector_helper.register(plugin_fn)


def uninitializePlugin(plugin):

    plugin_fn = om.MFnPlugin(plugin)
    angle_helper.deregister(plugin_fn)
    angle_cone_helper.deregister(plugin_fn)
    vector_helper.deregister(plugin_fn)


if __name__ == "__main__":
    import maya.cmds as cmds

    cmds.file(new=True, force=True)

    plugin_name = "maya_rigging_helpers.py"

    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(
            plugin_name
        )
    )
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(
            plugin_name
        )
    )
