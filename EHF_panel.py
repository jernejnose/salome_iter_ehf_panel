from salome.shaper import model
import SalomePyQt
from qtsalome import QFileDialog, QApplication


class Utils():
    def __init__(self, model, part):
        self.model = model
        self.part = part
        self.line_groups = 0
        self.point_groups = 0
        self.finger_group_count = 0

    def create_named_sketch(self, name, plane):
        '''
        Creates sketch on specified plane and names it
        '''
        sketch = self.model.addSketch(self.part, self.model.defaultPlane(plane))
        sketch.setName(name)
        sketch.result().setName(name)
        return sketch

    def create_closed_lines(self, sketch, point_array, offset=None, custom_prefix=None):
        '''
        Creates closed line that crosses points in array.
        :param sketch: sketch to draw on
        :param point_array: array of arrays point coordinates [[x,y,z],...]
        :param offset: translation of lines
        :param custom_prefix: custom name prefix for lines
        :return:  array with line names and line objects. [{name: line name, object: salome line object},]
        '''
        lines = []
        i = 0
        if offset is not None:
            for i in range(len(point_array)):
                point_array[i][0] = point_array[i][0] + offset[0]
                point_array[i][1] = point_array[i][1] + offset[1]
                i += 1
        i = 0
        for i in range(len(point_array)):
            line = sketch.addLine(point_array[i - 1][0], point_array[i - 1][1], point_array[i][0], point_array[i][1])
            if custom_prefix is not None:
                line_name = custom_prefix + "_l" + str(i)
            else:
                line_name = "g" + str(self.line_groups) + "_l" + str(i)
                self.line_groups += 1
            line.setName(line_name)
            line.result().setName(line_name)
            lines.append({"name": line_name, "object": line})
            i += 1
        self.model.do()
        self.line_groups += 1
        return lines

    def create_lines(self, sketch, point_array, offset=None, custom_prefix=None):
        '''
        Creates closed line that crosses points in array.
        :param sketch: sketch object to create lines on
        :param point_array: array of point coordinates [x,y]
        :param offset: offset of sketch origin
        :param custom_prefix: custom prefix for line names
        :return: array of line objects [{name: line name,object: salome_object},...]
        '''
        lines = []
        i = 0
        if offset is not None:
            for i in range(len(point_array)):
                point_array[i][0] = point_array[i][0] + offset[0]
                point_array[i][1] = point_array[i][1] + offset[1]
                point_array[i][2] = point_array[i][2] + offset[0]
                point_array[i][3] = point_array[i][3] + offset[1]
                i += 1

        i = 0
        for l in point_array:
            line = sketch.addLine(l[0], l[1], l[2], l[3])
            if custom_prefix is not None:
                line_name = custom_prefix + "_l" + str(i)
            else:
                line_name = "g" + str(self.line_groups) + "_l" + str(i)
                self.line_groups += 1            
            line.setName(line_name)
            line.result().setName(line_name)
            lines.append({"name": line_name, "object": line})
            i += 1
        self.model.do()
        return lines

    def face_from_line_names(self, names_array, face_name=None):
        '''
        Creates face from lines, lines are selected by names
        :param names_array: array of line names
        :param face_name: name of created face
        :return: salome face object
        '''
        face = self.model.addFace(self.part, [self.model.selection("EDGE", name) for name in names_array])
        if face_name != None:
            face.setName(face_name)
            face.result().setName(face_name)
        self.model.do()
        return face

    def face_from_selector(self, selector, face_name=None):
        '''
        Creates face from lines, lines are selected with selectors
        :param selector: line selector
        :param face_name: name of created face
        :return: face object {object: salome_object, selector: selector}
        '''
        face = self.model.addFace(self.part, [self.model.selection("FACE", selector)])
        if face_name != None:
            face.setName(face_name)
            face.result().setName(face_name)
        self.model.do()
        return {"object": face, "selector": self.model.selection("FACE", selector)}

    def create_3d_points(self, point_array, offset=None):
        '''
        Creates 3d points from array of coordinates
        :param point_array: array of coordinates [x,y,z]
        :param offset:
        :return:
        '''

        points = []
        i = 0
        if offset is not None:
            for l in point_array:
                point = self.model.addPoint(self.part, l[0] + offset[0], l[1] + offset[1], l[2] + offset[2])
                point_name = "p_g" + str(self.point_groups) + "_p" + str(i)
                point.setName(point_name)
                point.result().setName(point_name)
                points.append({"name": point_name, "object": point, "selector": self.model.selection("POINT", point_name)})
                i += 1
        else:
            for l in point_array:
                point = self.model.addPoint(self.part, l[0], l[1], l[2])
                point_name = "p_g" + str(self.point_groups) + "_p" + str(i)
                point.setName(point_name)
                point.result().setName(point_name)
                points.append({"name": point_name, "object": point, "selector": self.model.selection("POINT", point_name)})
                i += 1
        self.model.do()
        self.point_groups += 1
        return points

    def create_fingers(self, origin, number, column):
        '''
        Creates group of fingers at specified location
        :param origin: origin of first finger
        :param number: number of fingers
        :param column: number of panel column, currently supports only 0 and 1
        :return:
        '''
        # coordinates of points on wall of tokamak for each column of panels
        column_points = [
            [[0.0, 0.0, 0], [19.97716698999966, 166.71921320090001, 0], [14.343684899999971, 334.6958521369, 0],
             [-11.867176640000253, 500.7414190149, 0], [-63.509916440000325, 660.5546363679, 0],
             [-72.8771179800001, 682.8840037179, 0], [-71.71192124000027, 707.0705170549, 0],
             [-77.84264041999995, 874.9062219229, 0],[-110.00258320000012, 1039.9003087979, 0],
             [-162.16228961000024, 1199.6805879178999, 0], [-237.95511282000007, 1349.5105051978999, 0]],
            [[0.0, 0.0, 0], [-38.2489327899998, 163.49740791, 0], [-100.99406846000011, 319.41705163000006, 0],
             [-182.41515021999976, 466.48420291, 0],  [-285.6027912300001, 598.9966466999999, 0],[-302.0421748200001, 616.77561681, 0],
             [-309.21952280000005, 639.9020256700001, 0], [-372.3837062100001, 795.5191695899998, 0],
             [-459.03546835999987, 939.5635472600002, 0], [-562.6880246999999, 1071.8573278200001, 0],
             [-685.16444, 1186.73962162, 0]]]

        #create points to interpolate through
        pipe_points = self.create_3d_points(column_points[column], origin)

        # create interpolation line through points on wall
        pipe_line = self.model.addInterpolation(self.part, [point["selector"] for point in pipe_points],
                                                False,
                                                False)
        pipe_line.setName("rob" + str(self.finger_group_count))
        pipe_line.result().setName("rob" + str(self.finger_group_count))

        # create plane for sketch on edge of tokamak wall, plane is normal on interpolation line
        plane_line = self.model.addPolyline3D(self.part, [point["selector"] for point in pipe_points[:2]])
        plane_line.setName("normala" + str(self.finger_group_count))
        plane_line.result().setName("normala" + str(self.finger_group_count))
        pipe_plane = self.model.addPlane(self.part, self.model.selection("EDGE", "normala" + str(
            self.finger_group_count) + "/Generated_Edge&" + pipe_points[0]["name"] + "/" + pipe_points[0]["name"]), pipe_points[0]["selector"], True)
        pipe_plane.setName("plane0" + str(self.finger_group_count))
        pipe_plane.result().setName("plane0" + str(self.finger_group_count))

        # create sketch on new plane
        EHF_sketch = self.model.addSketch(self.part,
                                          self.model.selection("FACE", "plane0" + str(self.finger_group_count)))
        EHF_sketch.setName("EHF_sketch" + str(self.finger_group_count))
        EHF_sketch.result().setName("EHF_sketch" + str(self.finger_group_count))

        # because all sketches have same origin, we need to add offset (coordinates of first point of interpolation line - width of sketch)
        offset = [sqrt(origin[0]**2 + origin[1]**2) - 61.56, -origin[2] - 50]

        # create points for sketch
        EHF_sketch_points_1 = [[0, 0], [50, 0], [50, 30], [34, 30], [34, 23], [33, 23], [33, 30], [17, 30], [17, 23],
                               [16, 23], [16, 30], [0, 30]]
        # rotation of points, changes x to y and y to x
        EHF_sketch_points_1_inverted = [[p[1], p[0]] for p in EHF_sketch_points_1]

        EHF_sketch_points_2 = [[5, 5.5], [8, 5.5], [8, 11], [42, 11], [42, 5.5], [45, 5.5], [45, 19], [5, 19]]
        # rotation of points, changes x to y and y to x
        EHF_sketch_points_2_inverted = [[p[1], p[0]] for p in EHF_sketch_points_2]

        EHF_sketch_points_3 = [[0, 9, 5, 9], [0, 15, 5, 15], [0, 23, 50, 23], [45, 9, 50, 9], [45, 15, 50, 15]]
        # rotation of points, changes x to y and y to x
        EHF_sketch_points_3_inverted = [[p[1], p[0], p[3], p[2]] for p in EHF_sketch_points_3]

        # create lines from points
        EHF_sketch_lines_1 = self.create_closed_lines(EHF_sketch, EHF_sketch_points_1_inverted, offset, "fin{}0".format(self.finger_group_count))
        EHF_sketch_lines_2 = self.create_closed_lines(EHF_sketch, EHF_sketch_points_2_inverted, offset, "fin{}1".format(self.finger_group_count))
        EHF_sketch_lines_3 = self.create_lines(EHF_sketch, EHF_sketch_points_3_inverted, offset, "fin{}2".format(self.finger_group_count))

        # create faces
        EHF_faces_1 = []
        EHF_faces_1.append(self.face_from_selector("EHF_sketch{0}/Face-fin{0}2_l0f-fin{0}1_l0f-fin{0}1_l1f-fin{0}1_l2f-fin{0}1_l3f-fin{0}1_l4f-fin{0}1_l5f-fin{0}1_l6f-fin{0}2_l3f-fin{0}0_l2r-fin{0}0_l1r-fin{0}0_l0r".format(self.finger_group_count),
                                                   "face_1"))
        EHF_faces_1.append(
            self.face_from_selector("EHF_sketch{0}/Face-fin{0}2_l1f-fin{0}1_l0f-fin{0}2_l0r-fin{0}0_l0r".format(self.finger_group_count),
                                    "face_2"))
        EHF_faces_1.append(
            self.face_from_selector("EHF_sketch{0}/Face-fin{0}2_l3r-fin{0}1_l6f-fin{0}2_l4f-fin{0}0_l2r".format(self.finger_group_count),
                                    "face_3"))
        EHF_faces_1.append(self.face_from_selector("EHF_sketch{0}/Face-fin{0}2_l2f-fin{0}0_l9r-fin{0}2_l2f-fin{0}0_l5r-fin{0}2_l2f-fin{0}0_l2r-fin{0}2_l4r-fin{0}1_l6f-fin{0}1_l7f-fin{0}1_l0f-fin{0}2_l1r-fin{0}0_l0r".format(self.finger_group_count),
                                                   "face_4"))
        EHF_faces_1.append(
            self.face_from_selector("EHF_sketch{0}/Face-fin{0}0_l11r-fin{0}0_l10r-fin{0}2_l2r-fin{0}0_l0r".format(self.finger_group_count),
                                    "face_5"))
        EHF_faces_1.append(
            self.face_from_selector("EHF_sketch{0}/Face-fin{0}2_l2r-fin{0}0_l8r-fin{0}0_l7r-fin{0}0_l6r".format(self.finger_group_count),
                                    "face_6"))
        EHF_faces_1.append(
            self.face_from_selector("EHF_sketch{0}/Face-fin{0}2_l2r-fin{0}0_l4r-fin{0}0_l3r-fin{0}0_l2r".format(self.finger_group_count),
                                    "face_7"))

        # create shell
        EHF_sketch_shell_1 = self.model.addShell(self.part, [face['selector'] for face in EHF_faces_1])
        EHF_sketch_shell_1.setName("shell_1" + str(self.finger_group_count))
        EHF_sketch_shell_1.result().setName("shell_1" + str(self.finger_group_count))

        # create pipe
        cev = self.model.addPipe(self.part, [face['selector'] for face in EHF_faces_1],
                                 self.model.selection("EDGE", "rob{}".format(self.finger_group_count)))
        cev.setName("cev{}".format(self.finger_group_count))
        cev.result().setName("cev{}".format(self.finger_group_count))

        # copy pipes
        linear_copy_1_objects = [self.model.selection("SOLID", "Pipe_{}_1_{}".format(self.finger_group_count + 1, i)) for i in range(1,8)]
        self.model.addMultiTranslation(self.part, linear_copy_1_objects,
                                                      self.model.selection("EDGE", "PartSet/OZ"), 50, number)

        self.finger_group_count += 1


def getSTEPfileDialog():
    # Definiramo nastavitve za dialog
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    # Nastavimo in poženemo dialog
    STEPfilePath, ok = QFileDialog.getOpenFileName(None,
                                                   "Izberi STEP datoteko",
                                                   "",
                                                   "STEP datoteke (*.stp *.step *.STP *.STEP)",
                                                   options=options)
    # Vrnemo izbrano pot do datoteke
    return STEPfilePath


def openSTEPfile(filePath: str):
    # Importanje STEP datoteke na podlagi "filePath" spremenljivke
    Import_1 = model.addImport(part, filePath)

    # Posodobi prikaz modela
    model.do()


if __name__ == '__main__':
    # activate shaper module
    sgPyQt = SalomePyQt.SalomePyQt()
    sgPyQt.activateModule('Shaper')

    # initialize model
    model.begin()
    my_part_set = model.moduleDocument()

    # create part
    part = model.addPart(my_part_set).document()

    # initalze shaper utils with model and part
    sh_u = Utils(model, part)

    # import scaled step model of tokamak
    filePath = getSTEPfileDialog()
    # Odpri STEP file
    openSTEPfile(filePath)
    model.do()

    #create fingers for each panel from first column
    sh_u.create_fingers([4069.5122273, 21.8305981021, -381], 16, 0)
    sh_u.create_fingers([4069.5122273, 21.8305981021, 634], 16, 0)
    sh_u.create_fingers([4069.5122273, 21.8305981021, 1649], 16, 0)

    #create fingers for each panel from second column
    sh_u.create_fingers([3816.6241059, 1412.36920719, -381], 16, 1)
    sh_u.create_fingers([3816.6241059, 1412.36920719, 634], 16, 1)
    sh_u.create_fingers([3816.6241059, 1412.36920719, 1649], 16, 1)

    model.do()
