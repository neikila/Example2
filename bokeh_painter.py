from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.models.widgets import Button
from bokeh.plotting import figure, output_file, show, save
from Box2D import *
from startSettings import *
from datetime import datetime
import os

def append_rect_timestep(all_bodies_timesteps, rects):
  timestep = {'xs':[], 'ys':[], 'color':[]}
  for body in rects:
    timestep['xs'].append(body['x'])
    timestep['ys'].append(body['y'])
    timestep['color'].append(body['color'])
  all_bodies_timesteps['rects_timesteps'].append(timestep)


def points_to_dictionary(points, zero):
  result = {'x':[], 'y':[]}

  for p in points:
    result['x'].append(p[0] + zero.x)
    result['y'].append(p[1] + zero.y)

  return result


class Painter(object):

  def __init__(self, settings, model, max_iteration, size):
    self.max_iteration = max_iteration
    self.width = size
    self.height = size
    self.len_before_redunction = max_iteration
    self.start_settings = settings
    self.model = model

    self.init()

  def get_model_size(self):
    sett = self.start_settings
    ground_set = sett.ground_settings

    model_width = ground_set.get_right()[0] - ground_set.get_left()[0]

    model_height = model_width / 2
    return {'x': model_width, 'y': model_height}

  def init(self):
    self.reduced = False
    self.directory_to_save = "out/"
    
    # Adjusting size of pictire
    model_size = self.model_size = self.get_model_size()
    ground_set = self.start_settings.ground_settings

    scale = {
      'x': self.width / model_size['x'],
      'y': self.height / model_size['y']
      }

    if scale['x'] > scale['y']:
      scale['x'] = scale['y']
      self.width = model_size['x'] * scale['x']
    else:
      scale['y'] = scale['x']
      self.height = model_size['y'] * scale['y']

    self.local_zero_point = b2Vec2(
      -ground_set.get_left()[0],
      -ground_set.get_bottom()[1] 
      )

    # Preparing dictionary for Bokeh
    self.all_bodies = {'rects_timesteps':[], 'circles_timesteps':[], 'score':[]}
    # Preparing js-callback for Bokeh
    self.js_code = """
var cur_data = current.get('data');
var all_data = all_polyg.get('data');
var cur_circles = current_circles.get('data');
var text_data = text.get('data')

xs = cur_data['xs'];
ys = cur_data['ys'];
color = cur_data['color'];

var rect_next_to_show = all_data['rects_timesteps'][num];
n_xs = rect_next_to_show['xs'];
n_ys = rect_next_to_show['ys'];
n_color = rect_next_to_show['color'];

for (i = 0; i < n_xs.length; ++i) {
  xs[i] = n_xs[i];
  ys[i] = n_ys[i];
  color[i] = n_color[i];
}

delta = xs.length - n_xs.length;
if (delta > 0) {
  xs.splice(xs.length - delta, delta);
  ys.splice(ys.length - delta, delta);
  color.splice(color.length - delta, delta);
}

x = cur_circles['x']
y = cur_circles['y']
color = cur_circles['color']
radius = cur_circles['radius']

var circles_next_to_show = all_data['circles_timesteps'][num];
n_x = circles_next_to_show['x'];
n_y = circles_next_to_show['y'];
n_color = circles_next_to_show['color'];
n_radius = circles_next_to_show['radius'];

for (i = 0; i < n_x.length; ++i) {
  x[i] = n_x[i];
  y[i] = n_y[i];
  color[i] = n_color[i];
  radius[i] = n_radius[i];
}

delta = x.length - n_x.length;
if (delta > 0) {
  x.splice(x.length - delta, delta);
  y.splice(y.length - delta, delta);
  color.splice(color.length - delta, delta);
  radius.splice(radius.length - delta, delta);
}

text_data['score'][0] = 'Score ' + all_data['score'][num]

current.trigger('change');
current_circles.trigger('change');
text.trigger('change');
"""

  def get_trajectory_zero_point(self):
    return b2Vec2(
      self.local_zero_point.x,
      self.local_zero_point.y
      )

  def save_timestep(self):
    material_library = self.start_settings.material_library
    polygons = []
    circles = {'x':[], 'y':[], 'radius':[], 'color':[]}
    zero = self.local_zero_point
    for body in self.model.bodies:
      
      for fixture in body.fixtures:
        shape = fixture.shape

        if isinstance(shape, b2PolygonShape) and len(shape.vertices) > 2:
          polygon = {'x':[], 'y':[]}
          for vertice in shape.vertices:
            vertice = zero + body.GetWorldPoint(vertice)
            polygon['x'].append(vertice.x)
            polygon['y'].append(vertice.y)
            polygon['color'] = material_library.materials[body.material_type].color
          
          polygons.append(polygon)

        if isinstance(shape, b2CircleShape):
          center = zero + body.GetWorldPoint(shape.pos)
          circles['x'].append(center.x)
          circles['y'].append(center.y)
          circles['radius'].append(shape.radius)
          circles['color'].append(material_library.materials[body.material_type].color)

    self.all_bodies['circles_timesteps'].append(circles)
    self.all_bodies['score'].append(str(int(self.model.score)))
    append_rect_timestep(self.all_bodies, polygons)



  def create_html(self):
    self.reduce()
    temp = datetime.now()
    filename = temp.strftime("%y_%m_%d__%H_%M_%S_") + "{:0>6}".format(temp.microsecond) + ".html"
    output_file(self.directory_to_save + filename)
 
    current_position = ColumnDataSource(data={'num':[0]})
    flags = ColumnDataSource(data={'flag':[{'is_playing': False}]})
    text = ColumnDataSource(data=dict(score=['Score ' + self.all_bodies['score'][0]]))
    current_polyg = ColumnDataSource(data=self.all_bodies['rects_timesteps'][0])
    all_polyg = ColumnDataSource(data=self.all_bodies)
 
    current_circles = ColumnDataSource(data=self.all_bodies['circles_timesteps'][0])
    slider_callback = Callback(
        args=dict(
          current=current_polyg,
          current_circles=current_circles, 
          all_polyg=all_polyg,
          text=text,
          flags=flags,
          current_position=current_position
          ), 
        code="""
var num = cb_obj.get('value');
current_position.get('data')['num'][0] = num;
var flags_data = flags.get('data');
flags_data['flag']['is_playing'] = false;
flags.trigger('change');
current_position.trigger('change');
""" + self.js_code)
 
    slider = Slider(start=0, end=len(self.all_bodies['rects_timesteps']) - 1,
        value=0, step=1,
        title="Iteration number", callback=slider_callback)
    slider_id = '' + str(slider.vm_serialize()['id'])
 
    p = figure(
        plot_width=int(self.width), plot_height=int(self.height),
        x_range=(0, int(self.model_size['x'])), y_range=(0, int(self.model_size['y'])),
        title="Watch Here"
        )
 
    button_callback = Callback(
        args=dict(
          current=current_polyg,
          current_circles=current_circles, 
          all_polyg=all_polyg,
          text=text,
          flags=flags,
          current_position=current_position
          ), 
        code="""
console.log("Start");
var flags_data = flags.get('data');
var num = current_position.get('data')['num'][0]
var slider_id = '""" + slider_id + """'
var amount_of_iterations = """ + str(len(self.all_bodies['rects_timesteps'])) + """; 
if (!flags_data['flag']['is_playing']) {
  flags_data['flag']['is_playing'] = true
  intervalID = setInterval(function () {
  var flags_data = flags.get('data');
  is_playing = flags_data['flag']['is_playing']
    if (is_playing) {
      """ + self.js_code + """
      Bokeh.$('div #' + slider_id).val(Math.floor(num));
      Bokeh.$('div #' + slider_id + ' :first-child').css('left', num / (amount_of_iterations - 1) * 100 + '%')
      num += 1
    }
   
    if (num > (amount_of_iterations - 1) || !is_playing) {
      current_position.get('data')['num'][0] = num
      current_position.trigger('change')
      flags_data['flag']['is_playing'] = is_playing = false
      window.clearInterval(intervalID);
      console.log("Finally")
  }
  }, Math.floor(1000.0 / """ + str(self.start_settings.model_settings.hz / 10.0) + """ / """ + str((float(self.max_iteration) / self.len_before_redunction)) + """));
} else {
  flags_data['flag']['is_playing'] = false
}
flags.trigger('change')
return false;
""")
    button = Button(label="Play", type="success", callback=button_callback)
    ground = points_to_dictionary(self.start_settings.ground_settings.points,
        self.local_zero_point)
    p.line(ground['x'], ground['y'])
    p.patches('xs', 'ys', color='color', source=current_polyg)
    p.circle('x', 'y', radius='radius', color='color', source=current_circles)
    p.text(1, int(self.model_size['y']) - 3, text='score', alpha=5,
        text_font_size="15pt", text_baseline="middle", text_align="left",
        source=text)

    self.layout = vform(button, slider, p)

  def reduce(self):
    if self.reduced == False:
      self.len_before_redunction = current = len(self.all_bodies['score'])
      required = self.max_iteration
      diff = current - required

      to_remove = []
      if (diff > 0):
        number = []
        for i in range(current):
          number.append((i, abs((i * (float((required - 1)) / (current - 1))) % 1 - 0.5)))
        temp = [i[0] for i in sorted(number, key=itemgetter(1))[:diff]]
        temp = sorted(temp, reverse=True)
        for i in temp:
          del self.all_bodies['score'][i]
          del self.all_bodies['rects_timesteps'][i]
          del self.all_bodies['circles_timesteps'][i]

      self.reduced = True

  def save(self):
    self.reduce()
    save(self.layout)

  def show(self):
    self.reduce()
    show(self.layout)
