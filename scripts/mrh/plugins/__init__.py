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


def get_aim_matrix(origin, target, up_vector=om.MGlobal.upAxis()):
    """Return the aim matrix aiming from the origin to the target.

    The aim vector will be the Y Axis

    Args:
        origin(om.MPoint): origin point
        target(om.MPoint): target point
    """
    aim_vector = om.MVector(target - origin).normalize()

    if aim_vector.isParallel(up_vector):
        up_vector.x += 1
        up_vector.normalize()

    normal_vector = (aim_vector ^ up_vector).normalize()
    new_up_vector = (aim_vector ^ normal_vector).normalize()

    # fmt: off
    aim_matrix = om.MMatrix(
        [
            normal_vector.x,    normal_vector.y,    normal_vector.z,    0,
            aim_vector.x,       aim_vector.y,       aim_vector.z,       0,
            new_up_vector.x,    new_up_vector.y,    new_up_vector.z,    0,
            origin.x,           origin.y,           origin.z,           1,
        ]
    )
    # fmt: on
    return aim_matrix
