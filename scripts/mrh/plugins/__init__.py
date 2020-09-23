import maya.api.OpenMaya as om


class HelperData(om.MUserData):
    def __init__(self):
        super(HelperData, self).__init__(False)  ## don't delete after draw

        self.surface_color = om.MColor([1.0, 0.0, 0.0, 0.25])
        self.wire_color = om.MColor([1.0, 0.0, 0.0])

        self.points = om.MPointArray()
        self.triangles_indices = []
        self.lines_indices = []

    def get_line_points(self):
        array = om.MPointArray()
        for index in self.lines_indices:
            array.append(self.points[index])
        return array

    def get_triangle_points(self):
        array = om.MPointArray()
        for index in self.triangles_indices:
            array.append(self.points[index])
        return array
