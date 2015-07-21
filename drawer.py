#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide.QtGui import *
from PySide.QtCore import *
import xml.etree.ElementTree as ET
from Box2D import * 
from startSettings import *
from datetime import datetime

def get_qt_point_from_xml_point(point, scale):
  return QPoint(
      float(point.find('x').text) * scale.x(),
      -1 * float(point.find('y').text) * scale.y()
      )


def get_qt_point_from_tuple(point, scale):
  return QPoint(
      point[0] * scale.x(),
      -1 * point[1] * scale.y()
      )


def draw_lines_from_points(qp, points, scale, zero, transform, cicle=False):
  qt_points = []
  for p in points:
    qt_points.append(transform(p, scale))
  for start, finish in zip(qt_points[:-1], qt_points[1:]): 
    qp.drawLine(zero + start, zero + finish)
  if cicle == True:
    qp.drawLine(zero + qt_points[0], zero + qt_points[-1])


class WorldDrawer(QWidget):

  def get_model_size(self):
    sett = self.start_settings
    ground_set = sett.ground_settings

    model_width = ground_set.get_right()[0] - ground_set.get_left()[0]

    model_height = model_width / 2
    return QVector2D(model_width, model_height)

  def init(self):
    self.width = 800.0
    self.height = 800.0
    self.offset = QPoint(20, 20)
    # Create two are: one for text and another for trajectory. 
    self.text_area = QRect(
        self.offset.x() + 0, self.offset.y() + 0, 
        800, 40)
    # Setting trajectory area depended from text area
    self.trajectory_area = QRect(
        self.text_area.left() + 0, self.text_area.bottom() + 10, 
        800, 800
        )
    self.directory_to_save = "out/"
    
    model_size = self.get_model_size()
    ground_set = self.start_settings.ground_settings

    print "Model_size", model_size
    self.scale = QVector2D(
          self.trajectory_area.width() / model_size.x(), 
          self.trajectory_area.height() / model_size.y()
          )
    if self.scale.x() > self.scale.y():
      self.scale.setX(self.scale.y())
      self.trajectory_area.setWidth(model_size.x() * self.scale.x())
    else:
      self.scale.setY(self.scale.x())
      self.trajectory_area.setHeight(model_size.y() * self.scale.y())

    self.local_zero_point = QPoint(
        -self.scale.x() * ground_set.get_left()[0],
        -self.scale.y() * ground_set.get_bottom()[1] 
        )  

    # Getting resulting size of image
    self.total_area = QVector2D(
        max(self.text_area.right(), self.trajectory_area.right()) + self.offset.x(), 
        self.trajectory_area.bottom() + self.offset.y()
        )

  def __init__(self, settings, model):
    super(WorldDrawer, self).__init__()

    self.start_settings = settings
    self.model = model

    self.init()
    self.init_ui()
    
  def init_ui(self):    
    self.setGeometry(50, 50, self.total_area.x(), self.total_area.y())
    self.setWindowTitle('Result')
    self.show()

  def paintEvent(self, event):
    qp = QPainter()
    qp.begin(self)

    self.draw_image()
    qp.drawImage(0, 0, self.image)    

    qp.end()

  def draw_image(self, number=-1):
    self.image = QImage(self.total_area.x(), self.total_area.y(), QImage.Format_ARGB32)
    self.image.fill(qRgb(255, 255, 255))
    qp = QPainter()
    qp.begin(self.image)
    
    self.draw_ground(qp)
    for body in self.model.bodies:
      self.draw_body(qp, body)
    self.draw_text(qp, number)

    qp.end()

  def save_image(self):
    temp = datetime.now()
    filename = temp.strftime("%y_%m_%d__%H_%M_%S_") + "{:0>6}".format(temp.microsecond) + ".png"
    self.image.save(self.directory_to_save + filename)

  def get_trajectory_zero_point(self):
    return QPoint(
      self.trajectory_area.left() + self.local_zero_point.x(),
      self.trajectory_area.bottom() - self.local_zero_point.y()
      )

  def draw_ground(self, qp):
    scale = self.scale
    zero = self.get_trajectory_zero_point()

    draw_lines_from_points(
        qp, self.start_settings.ground_settings.points, 
        scale, zero, get_qt_point_from_tuple
        )

  def draw_body(self, qp, body):
    scale = self.scale
    zero = self.get_trajectory_zero_point()
    
    for fixture in body.fixtures:
      shape = fixture.shape
      if isinstance(shape, b2PolygonShape):
        polygon = QPolygon()
        for vertice in shape.vertices:
          polygon << zero + get_qt_point_from_tuple(body.GetWorldPoint(vertice).tuple,
              scale)
        qp.drawPolygon(polygon)
        
      if isinstance(shape, b2CircleShape):
        world_point = body.GetWorldPoint(shape.pos).tuple
        center = get_qt_point_from_tuple(world_point, scale)
        qp.drawEllipse(zero + center, shape.radius * scale.x(), shape.radius *
            scale.y())

    
  def draw_text(self, qp, number):
    rect = QRectF(self.text_area)
    if number >= 0:
      text = unicode(' Simulation\n Image number: {}'.format(number))
    else:
      text = unicode(' Simulation\n')
    qp.fillRect(rect, QColor(255, 255, 255))
    qp.setPen(QColor(168, 34, 3))
    qp.setFont(QFont('Decorative', 10))
    qp.drawText(rect, Qt.AlignLeft, text)        
    

def main(settings, model, show_image=False):
  ex = WorldDrawer(settings, model)
  ex.draw_image()
  #result = ex.save_image()
  if show_image == True:
    result = app.exec_()
  sys.exit(result)

