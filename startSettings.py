from operator import itemgetter
import xml.etree.ElementTree as ET


def get_points_from_xml(element_name, root_element):
  points = []
  element = root_element.find(element_name)
  for point in element.findall('point'):
    points.append((float(point[0].text), float(point[1].text)))
  return points


def get_polygon_from_xml(polygon):
  points = []
  for point in polygon.findall('point'):
    points.append((float(point[0].text), float(point[1].text)))
  return points


def get_point_from_xml(element_name, root_element):
  point = root_element.find(element_name)
  return (float(point[0].text), float(point[1].text))


def get_rectangle_from_xml(rectangle):
  points_el = rectangle.findall('point')
  polygon = []
  if len(points_el) != 0:
    p1 = (float(points_el[0][0].text), float(points_el[0][1].text))
    p2 = (float(points_el[1][0].text), float(points_el[1][1].text))
    polygon.append(p1)
    polygon.append((p1[0], p2[1]))
    polygon.append(p2)
    polygon.append((p2[0], p1[1]))
  else:
    width = float(rectangle.find('width').text)
    height = float(rectangle.find('height').text)
    polygon.append((0    , 0     ))
    polygon.append((width, 0     ))
    polygon.append((0    , height))
    polygon.append((width, height))
  return polygon

class Circle(object):
  
  def __init__(self, radius=0, pos=(0, 0)):
    self.radius = radius
    self.pos = pos


def get_circle_from_xml(circle):
  return Circle(
      float(circle.find('radius').text), 
      get_point_from_xml('position', circle)
      )
  

def get_objects_from_xml(element_name, subelement_name, root_element, handler):
  objects = []
  element = root_element.find(element_name)
  if element != None:
    for subelement in element.findall(subelement_name):
      objects.append(handler(subelement))
  return objects


def get_param(element_name, root_element, default_value):
  element = root_element.find(element_name)
  if element == None:
    return default_value
  else:
    return element.text


class Material(object):
  
  def __init__(self, name, impulse_scale, color):
    self.name = name
    self.impulse_scale = impulse_scale
    self.color = color

class MaterialBank(object):
  materials = []
  materials.append(Material('default', 0.2, (0, 0, 0)))
  materials.append(Material('wood', 0.7, (100, 100, 100)))
  materials.append(Material('metal', 0.3, (100, 100, 100)))
  materials.append(Material('projectile', 1, (100, 100, 100)))

  @staticmethod
  def get_material_by_name(name):
    for material in MaterialBank.materials:
      if material.name == name:
        return MaterialBank.materials.index(material)

class BodySettings(object):

  def __init__(self, body):
    self.lin_velocity_amplitude = float(get_param('lin_velocity_amplitude', body, 0))
    self.lin_velocity_angle = float(get_param('lin_velocity_angle', body, 0))
    self.angular_velocity = float(get_param('angular_velocity', body, 0))
    self.angle = float(get_param('angle', body, 0))
    shape = body.find('shape')
    self.circles = get_objects_from_xml(
        'circles', 'circle', shape, 
        get_circle_from_xml
        )
    self.polygons = get_objects_from_xml(
        'polygons', 'polygon', shape,
        get_polygon_from_xml
        )
    self.polygons += get_objects_from_xml(
        'rectangles', 'rectangle', shape,
        get_rectangle_from_xml
        )
    self.position = get_point_from_xml('position', body)
    self.is_dynamic = get_param('is_dynamic', body, 'True') == 'True'
    self.is_target = get_param('is_target', body, 'False') == 'True'
    self.health = float(get_param('health', body, 100))
    self.material_type = MaterialBank.get_material_by_name(get_param('material_type', body, 'default'))


def get_bodies_from_xml(element_name, root_element):
  bodies = []
  element = root_element.find(element_name)
  for body in element.findall('body'):
    bodies.append(BodySettings(body))
  return bodies


class BlockSettings(object):

  def __init__(self, block):
    self.block_position = get_point_from_xml('block_position', block) 
    self.bodies = get_bodies_from_xml('bodies', block)


class GroundSettings(object):

  def __init__(self, root_element):
    self.points = get_points_from_xml('vertices', root_element)
    self.left = min(self.points, key=itemgetter(0))
    self.right = max(self.points, key=itemgetter(0))
    self.bottom = min(self.points, key=itemgetter(1))

  def get_left(self):
    return self.left

  def get_right(self):
    return self.right

  def get_bottom(self):
    return self.bottom


class ModelSettings(object):

  def __init__(self, model):
    self.velocity_iterations = int(model.find('velocity_iterations').text)
    self.position_iterations = int(model.find('position_iterations').text)
    self.hz = float(model.find('hz').text)
    self.epsilon_lin_velocity = float(model.find('epsilon_lin_velocity').text)
    self.g = float(model.find('g').text)


class StartSettings(object):

  def __init__(self, filename='INPUT.dat'):
    self.getFromXML(filename)

  def getFromXML(self, filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    model = root.find('model')
    self.model_settings = ModelSettings(model)

    ground = root.find('ground')
    self.ground_settings = GroundSettings(ground)

    body = root.find('projectile')
    self.projectile_settings = BodySettings(body)

    blocks = root.find('blocks').findall('block')
    self.blocks = []
    for block in blocks:
      self.blocks.append(BlockSettings(block))
