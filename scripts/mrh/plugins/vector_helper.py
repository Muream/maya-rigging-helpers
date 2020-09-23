from __future__ import print_function

import logging
import math

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui
from mrh.plugins import HelperData

logger = logging.getLogger(__name__)


class VectorHelperNode(omui.MPxLocatorNode):
    TYPE_NAME = "vectorHelper"
    TYPE_ID = om.MTypeId(0x0007F76E)
    DRAW_CLASSIFICATION = "drawdb/geometry/vectorHelper"
    DRAW_REGISTRANT_ID = "VectorHelperNode"

    radius = None
    height = None
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
        unitFn.default = om.MDistance(1)
        unitFn.setMin(om.MDistance(0))
        om.MPxNode.addAttribute(VectorHelperNode.radius)

        VectorHelperNode.height = unitFn.create(
            "height", "h", om.MFnUnitAttribute.kDistance
        )
        unitFn.default = om.MDistance(1)
        unitFn.setMin(om.MDistance(0))
        unitFn.channelBox = True
        om.MPxNode.addAttribute(VectorHelperNode.height)

        numericFn = om.MFnNumericAttribute()
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

        radius = VectorHelperDrawOverride._get_radius(obj_path)
        height = VectorHelperDrawOverride._get_height(obj_path)
        cylinder_height = max(0, height - radius * 3)

        subdivisions = VectorHelperDrawOverride.subdivisions
        angle_offset = math.pi * 2 / subdivisions

        data.points.append(om.MPoint(0, 0, 0))
        # first circle
        for i in range(subdivisions):
            angle = i * angle_offset
            x = math.cos(angle) * radius
            y = 0
            z = math.sin(angle) * radius
            data.points.append(om.MPoint(x, y, z))

        # second circle
        for i in range(subdivisions):
            angle = i * angle_offset
            x = math.cos(angle) * radius
            y = cylinder_height
            z = math.sin(angle) * radius
            data.points.append(om.MPoint(x, y, z))

        # third circle
        for i in range(subdivisions):
            angle = i * angle_offset
            x = math.cos(angle) * radius * 2
            y = cylinder_height
            z = math.sin(angle) * radius * 2
            data.points.append(om.MPoint(x, y, z))

        data.points.append(om.MPoint(0, height, 0))

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
    def _get_radius(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, VectorHelperNode.radius)
        value = 1.0
        if not plug.isNull:
            value = plug.asMDistance().asCentimeters()

        return value

    @staticmethod
    def _get_height(obj_path):
        node = obj_path.node()
        plug = om.MPlug(node, VectorHelperNode.height)
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
            VectorHelperNode.TYPE_NAME,  # name of the node
            VectorHelperNode.TYPE_ID,  # unique id that identifies node
            VectorHelperNode.creator,  # function/method that returns new instance of class
            VectorHelperNode.initialize,  # function/method that will initialize all attributes of node
            om.MPxNode.kLocatorNode,  # type of node to be registered
            VectorHelperNode.DRAW_CLASSIFICATION,  # draw-specific classification string (VP2.0)
        )
    except:
        logger.error("Failed to register node: {0}".format(VectorHelperNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            VectorHelperNode.DRAW_CLASSIFICATION,  # draw-specific classification
            VectorHelperNode.DRAW_REGISTRANT_ID,  # unique name to identify registration
            VectorHelperDrawOverride.creator,  # function/method that returns new instance of class
        )
    except:
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
    except:
        logger.error(
            "Failed to deregister draw override: {0}".format(
                VectorHelperDrawOverride.NAME
            )
        )

    try:

        plugin_fn.deregisterNode(VectorHelperNode.TYPE_ID)
    except:
        logger.error(
            "Failed to deregister node: {0}".format(VectorHelperNode.TYPE_NAME)
        )


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

    cmds.evalDeferred('cmds.createNode("vectorHelper")')
