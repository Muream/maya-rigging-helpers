from __future__ import print_function

import logging
import math

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui
from mrh.plugins import HelperData, get_aim_matrix


logger = logging.getLogger(__name__)


class VectorHelperNode(omui.MPxLocatorNode):
    TYPE_NAME = "vectorHelper"
    TYPE_ID = om.MTypeId(0x00136202)
    DRAW_CLASSIFICATION = "drawdb/geometry/vectorHelper"
    DRAW_REGISTRANT_ID = "VectorHelperNode"

    radius = None

    origin = None
    target = None

    colorR = None
    colorG = None
    colorB = None

    def __init__(self):
        super(VectorHelperNode, self).__init__()

    @classmethod
    def creator(cls):
        return VectorHelperNode()

    @classmethod
    def initialize(cls):
        unitFn = om.MFnUnitAttribute()
        VectorHelperNode.radius = unitFn.create(
            "radius", "r", om.MFnUnitAttribute.kDistance
        )
        unitFn.channelBox = True
        unitFn.default = om.MDistance(0.1)
        unitFn.setMin(om.MDistance(0))
        om.MPxNode.addAttribute(VectorHelperNode.radius)

        numericFn = om.MFnNumericAttribute()

        VectorHelperNode.origin = numericFn.createPoint("origin", "o")
        numericFn.channelBox = True
        om.MPxNode.addAttribute(VectorHelperNode.origin)

        VectorHelperNode.target = numericFn.createPoint("target", "t")
        numericFn.channelBox = True
        om.MPxNode.addAttribute(VectorHelperNode.target)

        VectorHelperNode.colorR = numericFn.create(
            "colorR", "cr", om.MFnNumericData.kFloat, 1
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(VectorHelperNode.colorR)

        VectorHelperNode.colorG = numericFn.create(
            "colorG", "cg", om.MFnNumericData.kFloat, 0
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(VectorHelperNode.colorG)

        VectorHelperNode.colorB = numericFn.create(
            "colorB", "cb", om.MFnNumericData.kFloat, 0
        )
        numericFn.channelBox = True
        om.MPxNode.addAttribute(VectorHelperNode.colorB)


class VectorHelperDrawOverride(omr.MPxDrawOverride):
    NAME = "VectorHelperDrawOverride"

    subdivisions = 100

    def __init__(self, obj):
        super(VectorHelperDrawOverride, self).__init__(obj, None, True)

    def isTransparent(*args, **kwargs):
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, HelperData):
            data = HelperData()

        data.surface_color = VectorHelperDrawOverride._get_color(obj_path)
        data.surface_color.a = 0.25
        data.wire_color = VectorHelperDrawOverride._get_color(obj_path)
        data.points.clear()
        data.triangles_indices = []
        data.lines_indices = []

        data = self._generate_points(data, obj_path)
        data = self._generate_triangles(data)

        return data

    def _get_height(self, obj_path):
        origin = self._get_origin(obj_path)
        target = self._get_target(obj_path)

        aim_vector = om.MVector(target - origin)

        return aim_vector.length()

    def _generate_points(self, data, obj_path):
        origin = self._get_origin(obj_path)
        target = self._get_target(obj_path)
        aim_matrix = get_aim_matrix(origin, target)
        height = self._get_height(obj_path)

        radius = VectorHelperDrawOverride._get_radius(obj_path)
        subdivisions = VectorHelperDrawOverride.subdivisions
        angle_offset = math.pi * 2 / subdivisions
        cylinder_height = max(0, height - radius * 5)

        data.points.append(om.MPoint(0, 0, 0) * aim_matrix)
        # first circle
        for i in range(subdivisions):
            angle = i * angle_offset
            x = math.cos(angle) * radius
            y = 0
            z = math.sin(angle) * radius
            data.points.append(om.MPoint(x, y, z) * aim_matrix)

        # second circle
        for i in range(subdivisions):
            angle = i * angle_offset
            x = math.cos(angle) * radius
            y = cylinder_height
            z = math.sin(angle) * radius
            data.points.append(om.MPoint(x, y, z) * aim_matrix)

        # third circle
        for i in range(subdivisions):
            angle = i * angle_offset
            x = math.cos(angle) * radius * 3
            y = cylinder_height
            z = math.sin(angle) * radius * 3
            data.points.append(om.MPoint(x, y, z) * aim_matrix)

        data.points.append(om.MPoint(0, height, 0) * aim_matrix)
        return data

    def _generate_triangles(self, data):
        subdivisions = VectorHelperDrawOverride.subdivisions
        for i in range(len(data.points) - 1):
            data.lines_indices.append(i)
            data.lines_indices.append(i + 1)

        # base circle
        for i in range(subdivisions):
            p1 = 0
            p2 = i + 1
            if i == subdivisions - 1:
                p3 = 1
            else:
                p3 = i + 2
            data.triangles_indices.append(p1)
            data.triangles_indices.append(p2)
            data.triangles_indices.append(p3)

        # body cylinder
        for i in range(subdivisions):

            p1 = i + 1
            if i == subdivisions - 1:
                p2 = 1
            else:
                p2 = i + 2
            p3 = subdivisions + i + 1
            data.triangles_indices.append(p1)
            data.triangles_indices.append(p2)
            data.triangles_indices.append(p3)

            if i == subdivisions - 1:
                p1 = 1
                p2 = subdivisions + 1
            else:
                p1 = i + 2
                p2 = subdivisions + i + 2
            p3 = subdivisions + i + 1
            data.triangles_indices.append(p1)
            data.triangles_indices.append(p2)
            data.triangles_indices.append(p3)

        # body cylinder
        for i in range(subdivisions):

            p1 = subdivisions + i + 1
            if i == subdivisions - 1:
                p2 = subdivisions + 1
            else:
                p2 = subdivisions + i + 2
            p3 = subdivisions + subdivisions + i + 1
            data.triangles_indices.append(p1)
            data.triangles_indices.append(p2)
            data.triangles_indices.append(p3)

            if i == subdivisions - 1:
                p1 = subdivisions + 1
                p2 = subdivisions + subdivisions + 1
            else:
                p1 = subdivisions + i + 2
                p2 = subdivisions + subdivisions + i + 2
            p3 = subdivisions + subdivisions + i + 1
            data.triangles_indices.append(p1)
            data.triangles_indices.append(p2)
            data.triangles_indices.append(p3)

        # base circle
        for i in range(subdivisions):
            p1 = len(data.points) - 1
            p2 = subdivisions + subdivisions + i + 1
            if i == subdivisions - 1:
                p3 = subdivisions + subdivisions + 1
            else:
                p3 = subdivisions + subdivisions + i + 2
            data.triangles_indices.append(p1)
            data.triangles_indices.append(p2)
            data.triangles_indices.append(p3)

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
        return VectorHelperDrawOverride(obj)

    @staticmethod
    def _get_origin(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, VectorHelperNode.origin)
        x = plug.child(0).asFloat()
        y = plug.child(1).asFloat()
        z = plug.child(2).asFloat()

        return om.MPoint((x, y, z))

    @staticmethod
    def _get_target(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, VectorHelperNode.target)
        x = plug.child(0).asFloat()
        y = plug.child(1).asFloat()
        z = plug.child(2).asFloat()

        return om.MPoint((x, y, z))

    @staticmethod
    def _get_radius(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, VectorHelperNode.radius)
        value = 1.0
        if not plug.isNull:
            value = plug.asMDistance().asCentimeters()

        return value

    @staticmethod
    def _get_color(obj_path):
        node = obj_path.node()
        plug_r = om.MPlug(node, VectorHelperNode.colorR)
        plug_g = om.MPlug(node, VectorHelperNode.colorG)
        plug_b = om.MPlug(node, VectorHelperNode.colorB)
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
            VectorHelperNode.TYPE_NAME,
            VectorHelperNode.TYPE_ID,
            VectorHelperNode.creator,
            VectorHelperNode.initialize,
            om.MPxNode.kLocatorNode,
            VectorHelperNode.DRAW_CLASSIFICATION,
        )
    except Exception:
        logger.error("Failed to register node: {0}".format(VectorHelperNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            VectorHelperNode.DRAW_CLASSIFICATION,
            VectorHelperNode.DRAW_REGISTRANT_ID,
            VectorHelperDrawOverride.creator,
        )
    except Exception:
        logger.error(
            "Failed to register draw override: {0}".format(
                VectorHelperDrawOverride.NAME
            )
        )


def deregister(plugin_fn):
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            VectorHelperNode.DRAW_CLASSIFICATION, VectorHelperNode.DRAW_REGISTRANT_ID,
        )
    except Exception:
        logger.error(
            "Failed to deregister draw override: {0}".format(
                VectorHelperDrawOverride.NAME
            )
        )

    try:

        plugin_fn.deregisterNode(VectorHelperNode.TYPE_ID)
    except Exception:
        logger.error(
            "Failed to deregister node: {0}".format(VectorHelperNode.TYPE_NAME)
        )


if __name__ == "__main__":
    import maya.cmds as cmds

    cmds.file(new=True, force=True)

    plugin_name = "maya_rigging_helpers.py"

    if cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.unloadPlugin(plugin_name)
    if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.loadPlugin(plugin_name)

    vector_helper = cmds.createNode("vectorHelper")
    loc1 = cmds.spaceLocator()[0]
    loc2 = cmds.spaceLocator()[0]
    cmds.setAttr("locator2.translateY", 1)

    cmds.connectAttr("locator1.translate", "vectorHelper1.origin")
    cmds.connectAttr("locator2.translate", "vectorHelper1.target")
