from __future__ import print_function

import logging
import math

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui
from mrh.plugins import HelperData

logger = logging.getLogger(__name__)


class AngleConeHelperNode(omui.MPxLocatorNode):
    TYPE_NAME = "angleConeHelper"
    TYPE_ID = om.MTypeId(0x00136201)
    DRAW_CLASSIFICATION = "drawdb/geometry/angleConeHelper"
    DRAW_REGISTRANT_ID = "AngleConeHelperNode"

    height = None
    angle = None
    colorR = None
    colorG = None
    colorB = None

    def __init__(self):
        super(AngleConeHelperNode, self).__init__()

    @classmethod
    def creator(cls):
        return AngleConeHelperNode()

    @classmethod
    def initialize(cls):
        unitFn = om.MFnUnitAttribute()
        AngleConeHelperNode.height = unitFn.create(
            "height", "h", om.MFnUnitAttribute.kDistance
        )
        unitFn.default = om.MDistance(1)
        unitFn.setMin(om.MDistance(0))
        unitFn.channelBox = True
        om.MPxNode.addAttribute(AngleConeHelperNode.height)

        AngleConeHelperNode.angle = unitFn.create(
            "angle", "a", om.MFnUnitAttribute.kAngle
        )
        unitFn.default = om.MAngle(0)
        unitFn.setMin(om.MAngle(0))
        unitFn.setMax(om.MAngle(math.pi))
        unitFn.channelBox = True
        om.MPxNode.addAttribute(AngleConeHelperNode.angle)

        numericFn = om.MFnNumericAttribute()
        AngleConeHelperNode.colorR = numericFn.create(
            "colorR", "cr", om.MFnNumericData.kFloat, 1
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(AngleConeHelperNode.colorR)

        AngleConeHelperNode.colorG = numericFn.create(
            "colorG", "cg", om.MFnNumericData.kFloat, 0
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(AngleConeHelperNode.colorG)

        AngleConeHelperNode.colorB = numericFn.create(
            "colorB", "cb", om.MFnNumericData.kFloat, 0
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(AngleConeHelperNode.colorB)


class AngleConeHelperDrawOverride(omr.MPxDrawOverride):
    NAME = "AngleConeHelperDrawOverride"

    def __init__(self, obj):
        super(AngleConeHelperDrawOverride, self).__init__(obj, None, True)

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, HelperData):
            data = HelperData()

        data.surface_color = AngleConeHelperDrawOverride._get_color(obj_path)
        data.surface_color.a = 0.25
        data.wire_color = AngleConeHelperDrawOverride._get_color(obj_path)

        data.points.clear()
        data.triangles_indices = []
        data.lines_indices = []

        height = AngleConeHelperDrawOverride._get_height(obj_path)
        angle = AngleConeHelperDrawOverride._get_angle(obj_path)
        radius = math.tan(angle.asRadians() / 2) * height

        subdivisions = 100

        angle_offset = math.pi * 2 / subdivisions

        data.points.append(om.MPoint(0, 0, 0))
        for i in range(subdivisions + 1):
            angle = i * angle_offset
            x = math.cos(angle) * radius
            y = height
            z = math.sin(angle) * radius
            data.points.append(om.MPoint(x, y, z))

        for i in range(subdivisions):
            data.lines_indices.append(0)
            data.lines_indices.append(i + 1)
            data.lines_indices.append(i + 1)
            data.lines_indices.append(i + 2)

        for i in range(subdivisions):
            data.triangles_indices.append(0)
            data.triangles_indices.append(i + 1)
            data.triangles_indices.append(i + 2)

        return data

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        locatordata = data
        if not isinstance(locatordata, HelperData):
            return

        draw_manager.beginDrawable()

        draw_manager.setColor(locatordata.surface_color)
        draw_manager.setDepthPriority(5)

        if frame_context.getDisplayStyle() & omr.MFrameContext.kGouraudShaded:
            draw_manager.mesh(
                omr.MGeometry.kTriangles, locatordata.get_triangle_points()
            )

        if frame_context.getDisplayStyle() & omr.MFrameContext.kWireFrame:
            draw_manager.setColor(locatordata.wire_color)
            draw_manager.mesh(omr.MUIDrawManager.kLines, locatordata.get_line_points())

        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return AngleConeHelperDrawOverride(obj)

    @staticmethod
    def _get_height(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, AngleConeHelperNode.height)
        value = 1.0
        if not plug.isNull:
            value = plug.asMDistance().asCentimeters()

        return value

    @staticmethod
    def _get_angle(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, AngleConeHelperNode.angle)
        value = om.MAngle(0.0)
        if not plug.isNull:
            value = plug.asMAngle()

        return value

    @staticmethod
    def _get_color(obj_path):
        node = obj_path.node()
        plug_r = om.MPlug(node, AngleConeHelperNode.colorR)
        plug_g = om.MPlug(node, AngleConeHelperNode.colorG)
        plug_b = om.MPlug(node, AngleConeHelperNode.colorB)
        r, g, b = (1, 0, 0)
        if not plug_r.isNull:
            r = plug_r.asFloat()
        if not plug_g.isNull:
            g = plug_g.asFloat()
        if not plug_b.isNull:
            b = plug_b.asFloat()

        return om.MColor((r, g, b))


def register(plugin_fn):
    try:
        plugin_fn.registerNode(
            AngleConeHelperNode.TYPE_NAME,
            AngleConeHelperNode.TYPE_ID,
            AngleConeHelperNode.creator,
            AngleConeHelperNode.initialize,
            om.MPxNode.kLocatorNode,
            AngleConeHelperNode.DRAW_CLASSIFICATION,
        )
    except BaseException:
        logger.error(
            "Failed to register node: {0}".format(AngleConeHelperNode.TYPE_NAME)
        )

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            AngleConeHelperNode.DRAW_CLASSIFICATION,
            AngleConeHelperNode.DRAW_REGISTRANT_ID,
            AngleConeHelperDrawOverride.creator,
        )
    except BaseException:
        logger.error(
            "Failed to register draw override: {0}".format(
                AngleConeHelperDrawOverride.NAME
            )
        )


def deregister(plugin_fn):
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            AngleConeHelperNode.DRAW_CLASSIFICATION,
            AngleConeHelperNode.DRAW_REGISTRANT_ID,
        )
    except BaseException:
        logger.error(
            "Failed to deregister draw override: {0}".format(
                AngleConeHelperDrawOverride.NAME
            )
        )

    try:

        plugin_fn.deregisterNode(AngleConeHelperNode.TYPE_ID)
    except BaseException:
        logger.error(
            "Failed to deregister node: {0}".format(AngleConeHelperNode.TYPE_NAME)
        )


if __name__ == "__main__":
    import maya.cmds as cmds

    cmds.file(new=True, force=True)

    plugin_name = "maya_rigging_helpers.py"

    if cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.unloadPlugin(plugin_name)
    if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.loadPlugin(plugin_name)

    cmds.createNode("angleConeHelper")
    cmds.setAttr("angleConeHelper1.angle", 45)
