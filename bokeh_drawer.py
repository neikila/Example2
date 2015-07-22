from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show
from Box2D import * 

def append_timestep(bodies_all_timesteps, bodies):
  timestep = {'xs':[], 'ys':[], 'color':[]}
  for body in bodies:
    timestep['xs'].append(body['x'])
    timestep['ys'].append(body['y'])
    timestep['color'].append("#43a2ca")
  bodies_all_timesteps['timesteps'].append(timestep)

class Drawer(object):

  def __init__(self, settings, model):
    self.start_settings = settings
    self.model = model

    self.init()
    self.bodies_all_timesteps = {'timesteps':[]}

    # For test only
    body1 = {'x':[1, 3, 5], 'y':[1, 3, 1]}
    body2 = {'x':[6, 8, 10], 'y':[2, 4, 2]}
    bodies = [body1, body2]
    append_timestep(self.bodies_all_timesteps, bodies)

  def get_model_size(self):
    sett = self.start_settings
    ground_set = sett.ground_settings

    model_width = ground_set.get_right()[0] - ground_set.get_left()[0]

    model_height = model_width / 2
    return {'x': model_width, 'y': model_height}

  def init(self):
    self.width = 800.0
    self.height = 800.0
    
    model_size = self.model_size = self.get_model_size()
    ground_set = self.start_settings.ground_settings

    self.scale = {
      'x': self.width / model_size['x'],
      'y': self.height / model_size['y']
      }

    if self.scale['x'] > self.scale['y']:
      self.scale['x'] = self.scale['y']
      self.width = model_size['x'] * self.scale['x']
    else:
      self.scale['y'] = self.scale['x']
      self.height = model_size['y'] * self.scale['y']

    self.local_zero_point = b2Vec2(
      -ground_set.get_left()[0],
      -ground_set.get_bottom()[1] 
      )

  def get_trajectory_zero_point(self):
    return b2Vec2(
      self.local_zero_point.x,
      -self.local_zero_point.y
      )

  def save_timestep(self):
    polygons = []
    for body in self.model.bodies:
      zero = self.get_trajectory_zero_point()
      
      body_polygons = []
      for fixture in body.fixtures:
        shape = fixture.shape
        if isinstance(shape, b2PolygonShape) and len(shape.vertices) > 2:
          polygon = {'x':[], 'y':[]}
          for vertice in shape.vertices:
            vertice = zero + body.GetWorldPoint(vertice)
            polygon['x'].append(vertice.x)
            polygon['y'].append(vertice.y)
          
          body_polygons.append(polygon)

        if isinstance(shape, b2CircleShape):
          pass

      polygons += body_polygons

    append_timestep(self.bodies_all_timesteps, polygons)

  def create_html(self):
    output_file("callback.html")
 
    current_polyg = ColumnDataSource(data=self.bodies_all_timesteps['timesteps'][0])
    all_polyg = ColumnDataSource(data=self.bodies_all_timesteps)
 
    callback = Callback(args=dict(current=current_polyg, all_polyg=all_polyg), code="""
        var cur_data = current.get('data');
        var all_data = all_polyg.get('data');
        var f = cb_obj.get('value');
 
        xs = cur_data['xs'];
        ys = cur_data['ys'];
        color = cur_data['color'];
 
        var next_time_step = all_data['timesteps'][f];
        n_xs = next_time_step['xs'];
        n_ys = next_time_step['ys'];
        n_color = next_time_step['color'];
 
        for (i = 0; i < n_xs.length; ++i) {
          xs[i] = n_xs[i];
          ys[i] = n_ys[i];
          color[i] = n_color[i];
        }

        delta = xs.length - n_xs.length;
        if (delta > 0) {
          xs.splice(xs.length - delta, delta)
          ys.splice(ys.length - delta, delta)
          color.splice(color.length - delta, delta)
        }
 
        current.trigger('change');
        """)
 
    slider = Slider(start=0, end=len(self.bodies_all_timesteps['timesteps']) - 1,
        value=0, step=1,
        title="Iteration number", callback=callback)
 
    p = figure(
        plot_width=int(self.width), plot_height=int(self.height),
        x_range=(0, int(self.model_size['x'])), y_range=(0, int(self.model_size['y'])),
        tools="", title="Watch Here"
        )
 
    p.patches('xs', 'ys', 'color', source=current_polyg)
 
    self.layout = vform(slider, p)

  def show(self):
    show(self.layout)
