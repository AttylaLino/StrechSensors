import pyglet
from pyglet.gl import *
from sklearn.externals import joblib
import serial

window_height = 600
window_width = 1000
vert_line_place = 700
hor_line_place = window_height/2
info_margin = 30
graph_margin = 30
graph_width = vert_line_place - 2*graph_margin
graph_height = hor_line_place - 2*graph_margin
update_freq = 1/60

count = graph_margin
buffer = [graph_margin for element in list(range(0, graph_width))]
time = [graph_margin + element for element in list(range(0, graph_width))]
graph_points = []

strain = 0
resistence = 0
try:
    with serial.Serial('/dev/ttyUSB1', 19200, timeout=1) as ser:
        resistence = ser.read()
        sensor_status = '<font color=green>Active</font>'
except:
    sensor_status = '<font color=red>Not connected</font>'

model_name = 'neural_networks_model.pkl'
model = joblib.load(model_name)

window = pyglet.window.Window(width=window_width, height=window_height)
grid = pyglet.image.load('grid.png')
#Labels objects
lbl_graph_strain = pyglet.text.Label('Strain',
                          font_name='Times New Roman',
                          font_size=14,
                          x=0, y=0,
                          anchor_x='center', anchor_y='center')
lbl_graph_time = pyglet.text.Label('Time',
                          font_name='Times New Roman',
                          font_size=14,
                          x=350, y=graph_margin-7,
                          anchor_x='center', anchor_y='center')
lbl_graph_title = pyglet.text.Label('Real Time Strain Response',
                          font_name='Times New Roman',
                          font_size=18,
                          x=350, y=290,
                          anchor_x='center', anchor_y='center')
lbl_sensor_caption = pyglet.text.Label('Sensor Visualisation',
                          font_name='Times New Roman',
                          font_size=18,
                          x=350, y=375,
                          anchor_x='center', anchor_y='center')
lbl_title = pyglet.text.Label('Strech Sensor Interface',
                          font_name='Times New Roman',
                          font_size=24,
                          x=350, y=570,
                          anchor_x='center', anchor_y='center')
info = pyglet.text.HTMLLabel('',
                             width=window_width - vert_line_place,
                             multiline=True, anchor_x='left', anchor_y='top',
                             x=vert_line_place + info_margin, y=window_height - info_margin)
def update(dt):
    global strain
    if strain > 100:
        strain = 0
    strain += 1
    add_value_buffer(scale(strain,0,100,graph_margin,graph_margin+graph_height))
    #Add Serial reading part
    #Add Model prediction part

pyglet.clock.schedule_interval(update,update_freq)

@window.event
def on_draw():
    window.clear()
    glLoadIdentity()
    pyglet.gl.glColor3f(1.0, 1.0, 1.0)
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (0, hor_line_place, vert_line_place, hor_line_place)))
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (vert_line_place, 0, vert_line_place, window_height)))
    lbl_title.draw()
    draw_sensor()
    draw_dashboard()
    draw_graph()

def draw_sensor():
    # Strain Rectangle
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                         ('v2f', sensor_points(strain))
                         )
    lbl_sensor_caption.draw()

def draw_graph():
    #Graph
    #pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
    #                     ('v2f', [graph_margin, graph_margin, vert_line_place-graph_margin,
    #                              graph_margin, vert_line_place-graph_margin,
    #                              hor_line_place-graph_margin, graph_margin, hor_line_place-graph_margin])
    #                     )
    pyglet.gl.glColor3f(1.0, 1.0, 1.0)
    grid.blit(graph_margin, graph_margin, width=graph_width, height=graph_height)
    pyglet.gl.glColor3f(1.0, 0.0, 0.0)
    graph_points = []
    for i in list(range(0, graph_width)):
        graph_points.append(time[i])
        graph_points.append(buffer[i])
    pyglet.graphics.draw(graph_width, pyglet.gl.GL_POINTS, ('v2i', graph_points))
    lbl_graph_time.draw()
    lbl_graph_title.draw()
    glTranslatef(graph_margin-14, 150, 0.0)
    glRotatef(90.0, 0.0, 0.0, 1.0)
    lbl_graph_strain.draw()
    glLoadIdentity()

def draw_dashboard():
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                         ('v2f', [700, 300, 1000, 300, 1000, 600, 700, 600])
                         )
    global sensor_status, model, resistence, strain
    info_str = '''
    <h2>Sensor Information</h2>
    <p>Sensor Status: ''' + sensor_status + '''
    <p>Model: ''' + model_name + '''
    <h2>Sensor Data</h2> 
    <p> Resistence: ''' + str(resistence) + ''' 
    <p> Strain: ''' + str(strain)
    info.text = info_str
    info.draw()

def add_value_buffer(value):
    global buffer
    for i in range(0,len(buffer)-1):
        buffer[i] = buffer[i+1]
    buffer[len(buffer)-1] = value

def scale(x, min_x, max_x, min_scale, max_scale):
    return round((x - min_x) * (max_scale - min_scale) / (max_x - min_x) + min_scale)

sensor_center = [350, 450]
sensor_height = 100
def sensor_points(strain_value):
    #sensor relax 400, max strain 600
    global sensor_center, sensor_height
    width = scale(strain_value,0,100,400,600)
    return [sensor_center[0] - (width / 2), sensor_center[1] - (sensor_height / 2),
            sensor_center[0] + (width / 2), sensor_center[1] - (sensor_height / 2),
            sensor_center[0] + (width / 2), sensor_center[1] + (sensor_height / 2),
            sensor_center[0] - (width / 2), sensor_center[1] + (sensor_height / 2)]

#pyglet.gl.glClearColor(0, 0, 0, 0)
pyglet.app.run()
