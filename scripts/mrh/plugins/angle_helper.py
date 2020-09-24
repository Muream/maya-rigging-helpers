from __future__ import print_function

import logging
import math

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui
from mrh.plugins import HelperData

logger = logging.getLogger(__name__)


class AngleHelperNode(omui.MPxLocatorNode):
    TYPE_NAME = "angleHelper"
    TYPE_ID = om.MTypeId(0x0007F7F8)
    DRAW_CLASSIFICATION = "drawdb/geometry/angleHelper"
    DRAW_REGISTRANT_ID = "AngleHelperNode"

    radius1 = None
    radius2 = None
    angle1 = None
    angle2 = None
    colorR = None
    colorG = None
    colorB = None

    def __init__(self):
        super(AngleHelperNode, self).__init__()

    @classmethod
    def creator(cls):
        return AngleHelperNode()

    @classmethod
    def initialize(cls):
        unitFn = om.MFnUnitAttribute()
        AngleHelperNode.radius1 = unitFn.create(
            "radius1", "r1", om.MFnUnitAttribute.kDistance
        )
        unitFn.channelBox = True
        unitFn.default = om.MDistance(0)
        unitFn.setMin(om.MDistance(0))
        om.MPxNode.addAttribute(AngleHelperNode.radius1)

        AngleHelperNode.radius2 = unitFn.create(
            "radius2", "r2", om.MFnUnitAttribute.kDistance
        )
        unitFn.default = om.MDistance(1)
        unitFn.setMin(om.MDistance(0))
        unitFn.channelBox = True
        om.MPxNode.addAttribute(AngleHelperNode.radius2)

        AngleHelperNode.angle1 = unitFn.create(
            "angle1", "a1", om.MFnUnitAttribute.kAngle
        )
        unitFn.default = om.MAngle(0)
        unitFn.channelBox = True
        om.MPxNode.addAttribute(AngleHelperNode.angle1)

        AngleHelperNode.angle2 = unitFn.create(
            "angle2", "a2", om.MFnUnitAttribute.kAngle
        )
        unitFn.default = om.MAngle(0)
        unitFn.channelBox = True
        om.MPxNode.addAttribute(AngleHelperNode.angle2)

        numericFn = om.MFnNumericAttribute()
        AngleHelperNode.colorR = numericFn.create(
            "colorR", "cr", om.MFnNumericData.kFloat, 1
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(AngleHelperNode.colorR)

        AngleHelperNode.colorG = numericFn.create(
            "colorG", "cg", om.MFnNumericData.kFloat, 0
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(AngleHelperNode.colorG)

        AngleHelperNode.colorB = numericFn.create(
            "colorB", "cb", om.MFnNumericData.kFloat, 0
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(AngleHelperNode.colorB)


class AngleHelperDrawOverride(omr.MPxDrawOverride):
    NAME = "AngleHelperDrawOverride"

    subdivisions = 100

    def __init__(self, obj):
        super(AngleHelperDrawOverride, self).__init__(obj, None, True)

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, HelperData):
            data = HelperData()

        data.surface_color = AngleHelperDrawOverride._get_color(obj_path)
        data.surface_color.a = 0.25
        data.wire_color = AngleHelperDrawOverride._get_color(obj_path)
        data.points.clear()
        data.triangles_indices = []
        data.lines_indices = []

        radius1 = AngleHelperDrawOverride._get_radius1(obj_path)
        radius2 = AngleHelperDrawOverride._get_radius2(obj_path)
        angle1 = AngleHelperDrawOverride._get_angle1(obj_path)
        angle2 = AngleHelperDrawOverride._get_angle2(obj_path)
        angle = angle2.asRadians() - angle1.asRadians()

        subdivisions = AngleHelperDrawOverride.subdivisions
        angle_offset = angle / subdivisions

        # first circle
        for i in range(subdivisions + 1):
            angle = i * angle_offset + angle1.asRadians()
            x = math.cos(angle)
            y = 0
            z = math.sin(angle)
            data.points.append(om.MPoint(x, y, z) * radius1)

        # second circle
        for i in range(subdivisions + 1):
            angle = i * angle_offset + angle1.asRadians()
            x = math.cos(angle)
            y = 0
            z = math.sin(angle)
            data.points.append(om.MPoint(x, y, z) * radius2)

        data.lines_indices.append(0)
        data.lines_indices.append(subdivisions + 1)
        for i in range(subdivisions):
            data.lines_indices.append(i)
            data.lines_indices.append(i + 1)

        for i in range(subdivisions):
            data.lines_indices.append(subdivisions + i + 1)
            data.lines_indices.append(subdivisions + i + 2)
        data.lines_indices.append(subdivisions)
        data.lines_indices.append(subdivisions * 2 + 1)

        for i in range(subdivisions):
            data.triangles_indices.append(i)
            data.triangles_indices.append(i + 1)
            data.triangles_indices.append(subdivisions + i + 1)

            data.triangles_indices.append(subdivisions + i + 1)
            data.triangles_indices.append(subdivisions + i + 2)
            data.triangles_indices.append(i + 1)

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

        angle1 = AngleHelperDrawOverride._get_angle1(obj_path).asDegrees()
        angle2 = AngleHelperDrawOverride._get_angle2(obj_path).asDegrees()
        angle = angle2 - angle1

        a = data.points[0]
        b = data.points[AngleHelperDrawOverride.subdivisions + 2]
        distance_to_a = a.distanceTo(om.MPoint(0, 0, 0))
        distance_to_b = b.distanceTo(om.MPoint(0, 0, 0))
        if distance_to_a >= distance_to_b:
            text_pos = a
        else:
            text_pos = b

        text_pos *= 1.1
        text_color = om.MColor((0.1, 0.8, 0.8, 1))
        draw_manager.setColor(text_color)
        if angle == int(angle):
            text = "{} degrees".format(int(angle))
        else:
            text = "{0:.3f} degrees".format(angle)
        draw_manager.text(text_pos, text)
        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return AngleHelperDrawOverride(obj)

    @staticmethod
    def _get_radius1(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, AngleHelperNode.radius1)
        value = 1.0
        if not plug.isNull:
            value = plug.asMDistance().asCentimeters()

        return value

    @staticmethod
    def _get_radius2(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, AngleHelperNode.radius2)
        value = 1.0
        if not plug.isNull:
            value = plug.asMDistance().asCentimeters()

        return value

    @staticmethod
    def _get_angle1(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, AngleHelperNode.angle1)
        value = om.MAngle(0.0)
        if not plug.isNull:
            value = plug.asMAngle()

        return value

    @staticmethod
    def _get_angle2(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, AngleHelperNode.angle2)
        value = om.MAngle(0.0)
        if not plug.isNull:
            value = plug.asMAngle()

        return value

    @staticmethod
    def _get_color(obj_path):
        node = obj_path.node()
        plug_r = om.MPlug(node, AngleHelperNode.colorR)
        plug_g = om.MPlug(node, AngleHelperNode.colorG)
        plug_b = om.MPlug(node, AngleHelperNode.colorB)
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
            AngleHelperNode.TYPE_NAME,
            AngleHelperNode.TYPE_ID,
            AngleHelperNode.creator,
            AngleHelperNode.initialize,
            om.MPxNode.kLocatorNode,
            AngleHelperNode.DRAW_CLASSIFICATION,
        )
    except Exception:
        logger.error("Failed to register node: {0}".format(AngleHelperNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            AngleHelperNode.DRAW_CLASSIFICATION,
            AngleHelperNode.DRAW_REGISTRANT_ID,
            AngleHelperDrawOverride.creator,
        )
    except Exception:
        logger.error(
            "Failed to register draw override: {0}".format(AngleHelperDrawOverride.NAME)
        )


def deregister(plugin_fn):
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            AngleHelperNode.DRAW_CLASSIFICATION, AngleHelperNode.DRAW_REGISTRANT_ID,
        )
    except Exception:
        logger.error(
            "Failed to deregister draw override: {0}".format(
                AngleHelperDrawOverride.NAME
            )
        )

    try:
        plugin_fn.deregisterNode(AngleHelperNode.TYPE_ID)
    except Exception:
        logger.error("Failed to deregister node: {0}".format(AngleHelperNode.TYPE_NAME))


if __name__ == "__main__":
    import maya.cmds as cmds

    cmds.file(new=True, force=True)

    plugin_name = "maya_rigging_helpers.py"

    if cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.unloadPlugin(plugin_name)
    if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.loadPlugin(plugin_name)

    cmds.createNode("angleHelper")
    cmds.setAttr("angleHelper1.angle2", 90)
