#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

import xml.etree.ElementTree as ET

from startSettings import *
from simulation import *
from bokeh_drawer import *


def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i


def create_not_cycled_chain_shape(points):
  shapes = []
  for p1, p2 in zip(points[:-1:1], points[1::1]):
    shapes.append(b2EdgeShape(vertices=[p1, p2]))
  return shapes


def create_polygon_shapes(polygons):
  shapes = []
  for polygon in polygons:
    shapes.append(b2PolygonShape(vertices=polygon))
  return shapes


def create_circle_shapes(circles):
  shapes = []
  for circle in circles:
    shapes.append(b2CircleShape(radius=circle.radius, pos=circle.pos))
  return shapes


def create_shapes(body):
  shapes = []
  shapes += create_polygon_shapes(body.polygons)
  shapes += create_circle_shapes(body.circles)
  return shapes


class Throwable(Simulation):
  iteration_number = 0

  def save_final_state(self):
    sett = self.start_settings
    
    blocks = ET.SubElement(self.result_tree, "blocks")
    block = ET.SubElement(blocks, "block")

    vertice = ET.SubElement(block, "block_position")
    x = ET.SubElement(vertice, "x")
    x.text = str(0)
    
    y = ET.SubElement(vertice, "y")
    y.text = str(0)

    bodies = ET.SubElement(block, "bodies")
    for body in self.bodies:
      body_el = ET.SubElement(bodies, "body")

      lin_velocity_amplitude = ET.SubElement(body_el, "lin_velocity_amplitude")
      lin_velocity_amplitude.text = str(body.linearVelocity.length)

      lin_velocity_angle = ET.SubElement(body_el, "lin_velocity_angle")
      if body.linearVelocity.x != 0:
        angle = math.atan(body.linearVelocity.y / body.linearVelocity.x)
      else:
        angle = 0
      lin_velocity_angle.text = str(angle)

      angular_velocity = ET.SubElement(body_el, "angular_velocity")
      angular_velocity.text = str(body.angularVelocity)

      material_type = ET.SubElement(body_el, "material_type")
      material_type.text = sett.material_library.materials[body.material_type].name

      is_projectile = ET.SubElement(body_el, "is_projectile")
      is_projectile.text = str(False)
  
      world_point = body.GetWorldPoint(body.position)
      vertice = ET.SubElement(body_el, "position")
      x = ET.SubElement(vertice, "x")
      x.text = str(world_point.x)
      
      y = ET.SubElement(vertice, "y")
      y.text = str(world_point.y)
    
      angle = ET.SubElement(body_el, "angle")
      angle.text = str(body.angle)

      is_target = ET.SubElement(body_el, "is_target")
      is_target.text = str(body.is_target)
  
      is_dynamic = ET.SubElement(body_el, "is_dynamic")
      is_dynamic.text = str(body.is_dynamic)
  
      health = ET.SubElement(body_el, "health")
      health.text = str(body.health)

      polygons = None
      circles = None
      for fixture in body.fixtures:
        shape = fixture.shape
        shape_el = ET.SubElement(body_el, "shape")
        if isinstance(shape, b2PolygonShape):
          if polygons is None:
            polygons = ET.SubElement(shape_el, "polygons")
          polygon = ET.SubElement(polygons, 'polygon')
          for vertice in shape.vertices:
            world_point = self.body.GetWorldPoint(vertice)
            vertice = ET.SubElement(polygon, "point")
            x = ET.SubElement(vertice, "x")
            x.text = str(world_point.x)
            
            y = ET.SubElement(vertice, "y")
            y.text = str(world_point.y)

        if isinstance(shape, b2CircleShape):
          if circles is None:
            circles = ET.SubElement(shape_el, "circles")
          circle = ET.SubElement(circles, 'circle')
          world_point = body.GetWorldPoint(shape.pos)
          vertice = ET.SubElement(circle, "position")
          x = ET.SubElement(vertice, "x")
          x.text = str(world_point.x)
          
          y = ET.SubElement(vertice, "y")
          y.text = str(world_point.y)
          
          radius = ET.SubElement(circle, "radius")
          radius.text = str(shape.radius)

    result = ET.SubElement(self.result_tree, "result")
    score = ET.SubElement(result, "score")
    score.text = str(self.score)


  def convert_body_settings_to_body(self, body, offset=(0, 0)):
    if body.is_dynamic == True:
      func = self.world.CreateDynamicBody
    else:
      func = self.world.CreateStaticBody
    block = func(
          position=(
            offset[0] + body.position[0],
            offset[1] + body.position[1]
            ),
          angle=body.angle,
          shapes=create_shapes(body),
          shapeFixture=b2FixtureDef(density=1),
          angularVelocity=body.angular_velocity,
          linearVelocity=(
              body.lin_velocity_amplitude *
              math.cos(body.lin_velocity_angle),
              body.lin_velocity_amplitude *
              math.sin(body.lin_velocity_angle)
            )
        )
    block.is_dynamic = body.is_dynamic
    block.health = body.health
    block.material_type = body.material_type
    block.is_target = body.is_target
    block.is_projectile = body.is_projectile
    block.price = body.price
    self.bodies.append(block)
    return block

  def __init__(self, start_settings):

    # Initialising settings
    # It should be the first to execute
    sett = self.start_settings = start_settings

    self.init_world()
    self.world.gravity=b2Vec2(0, -1 * sett.model_settings.g)

    # Ground
    self.world.CreateBody(
          shapes=create_not_cycled_chain_shape(sett.ground_settings.points)
        )

    # Blocks
    self.bodies = []
    for block in sett.blocks:
      block_position = block.block_position
      for body in block.bodies:
        block = self.convert_body_settings_to_body(body, block_position)

    # Projectile(s)
    body = sett.projectile_settings
    self.body = self.convert_body_settings_to_body(body)
    self.shapes = create_shapes(body)
    self.fixtures = self.body.fixtures
    self.mass_data = b2MassData()

    # Create output xml tree
    self.result_tree = ET.Element("data")
    self.finalized = False

    # Function
    self.score = 0

    # Drawer
    self.ex = Drawer(self.start_settings, self)
    self.ex.save_timestep()

  def reduce_health(self, body, impulse):
    impulse_sum = sum(impulse.normalImpulses)
    if impulse_sum > 10:
      before = body.health
      reduction = self.start_settings.material_library.materials[body.material_type].impulse_scale * impulse_sum
      reduction = min(reduction, body.health) 
      self.score += body.price * reduction
      body.health -= reduction

  def analyze_body(self, body, opposite_body, impulse):
    body_extended = None
    if body in self.bodies:
      index = self.bodies.index(body)
      body_extended = self.bodies[index]
    if body == self.body:
      body_extended = self.body

    if body_extended != None:
      self.reduce_health(body_extended, impulse)

  def PostSolve(self, contact, impulse): 
    self.analyze_body(contact.fixtureA.body, contact.fixtureB.body, impulse)
    self.analyze_body(contact.fixtureB.body, contact.fixtureA.body, impulse)

  def Keyboard(self, key):
    pass

  def Step(self, settings):
    self.step_world(settings)
    
    self.iteration_number += 1
    if self.iteration_number % 10 == 0:
      self.ex.save_timestep()
    self.is_finished()
    self.check_health(self.bodies)
    self.check_health([self.body])

  # Actions to do in the end
  def finalize(self):
    if self.finalized == False:
      self. save_final_state()
      indent(self.result_tree)
      tree = ET.ElementTree(self.result_tree)
      tree.write('OUTPUT.dat')
      print "Score: {}".format(self.score)
      self.finalized = True
      self.ex.create_html()
      if not self.namespace.nosave:
        self.ex.save()
      if self.namespace.show:
        self.ex.show()

     
  def check_health(self, array):
    for el in array:
      if el.health <= 0:
        array.remove(el)
        self.world.DestroyBody(el)

  def has_object_finished(self, body):
    pos = body.position
    left = self.start_settings.ground_settings.get_left()
    right = self.start_settings.ground_settings.get_right()
    bottom = self.start_settings.ground_settings.get_bottom()
    
    if pos[0] < left[0] or pos[0] > right[0] or pos[1] < bottom[1]:
      self.world.DestroyBody(body)
      self.bodies.remove(body)
      return True
    
    velocity = body.linearVelocity
    accuracy = self.start_settings.model_settings.epsilon_lin_velocity
    if velocity.lengthSquared < accuracy ** 2:
      body.linearVelocity = b2Vec2(0, 0)
      return True


  # Should modelling be stopped
  def is_finished(self):
    if self.finalized == False:
      result = True
      for body in self.bodies:
        result = result and self.has_object_finished(body)
      if result == True:
        print "Finishing modelling"
        self.finalize()


if __name__=="__main__":
  start_settings = StartSettings()
  world = Throwable(start_settings)
  world.run()
  world.finalize()
