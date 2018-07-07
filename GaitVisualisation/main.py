import pyglet
from pyglet.gl import *
from sklearn.externals import joblib
import serial
from math import pi, sin, cos, ceil

window_width = 1200
info_margin = 20
graph_margin = 30
update_freq = 1/60

window_height = ceil(9*window_width/16)
vert_line_place = ceil(3*window_width/5)
hor_line_place = window_height/2
graph_width = vert_line_place - 2*graph_margin
graph_height = hor_line_place - 2*graph_margin

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

window = pyglet.window.Window(height = window_height, width = window_width,
                              caption='Gait Visualisation Interface')
grid = pyglet.image.load('grid.png')
key = pyglet.image.load('key.png')
#Labels objects
lbl_graph_strain = pyglet.text.Label('Strain',
                          font_name='Times New Roman',
                          font_size=14,
                          x=0, y=0,
                          anchor_x='center', anchor_y='center')
lbl_graph_time = pyglet.text.Label('Time',
                          font_name='Times New Roman',
                          font_size=14,
                          x=vert_line_place/2, y=graph_margin-7,
                          anchor_x='center', anchor_y='center')
lbl_graph_title = pyglet.text.Label('Real Time Strain Response',
                          font_name='Times New Roman',
                          font_size=18,
                          x=vert_line_place/2, y= hor_line_place - graph_margin/2,
                          anchor_x='center', anchor_y='center')
lbl_sensor_caption = pyglet.text.Label('Sensor Visualisation',
                          font_name='Times New Roman',
                          font_size=18,
                          x=vert_line_place/2, y=375,
                          anchor_x='center', anchor_y='center')
lbl_title = pyglet.text.Label('Strech Sensor Interface',
                          font_name='Times New Roman',
                          font_size=24,
                          x=vert_line_place/2, y=570,
                          anchor_x='center', anchor_y='center')
lbl_gait_title = pyglet.text.Label('Gait Visualisation',
                          font_name='Times New Roman',
                          font_size=24,
                          x=vert_line_place + (window_width - vert_line_place)/2, y=window_height - 20,
                          anchor_x='center', anchor_y='center')
dev_info = pyglet.text.HTMLLabel('',
                             width=window_width - vert_line_place,
                             multiline=True, anchor_x='left', anchor_y='top',
                             x= info_margin, y=window_height - info_margin)
gait_parameters = pyglet.text.HTMLLabel('',
                             width=window_width - vert_line_place,
                             multiline=True, anchor_x='left', anchor_y='top',
                             x= info_margin + vert_line_place/2, y=window_height - info_margin)
inc = True
def update(dt):
    global strain,inc
    if strain > 100:
        inc = False
    elif strain < 1:
        inc = True

    if inc == True:
        strain += 1
    else:
        strain -= 1

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
    draw_dashboard()
    draw_graph()
    draw_gait()


def draw_graph():
    pyglet.gl.glColor3f(1.0, 1.0, 1.0)
    grid.blit(graph_margin , graph_margin, width=graph_width, height=graph_height)
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
                         ('v2f', [0, hor_line_place,
                                  vert_line_place, hor_line_place,
                                  vert_line_place, window_height,
                                  0, window_height])
                         )
    global sensor_status, model, resistence, strain
    dev_info_str = '''
    <h2>Device Information</h2>
    <p>Sensor Status: ''' + sensor_status + '''
    <p>Model: ''' + model_name + '''
    <h2>Sensors Data</h2> 
    <p> Resistences: ''' + str(resistence) + ''' 
    <p> Strains: ''' + str(strain)

    gait_parameters_str = '''
       <h2>Gait Parameters</h2>
       <p>'''
    dev_info.text = dev_info_str
    dev_info.draw()
    gait_parameters.text = gait_parameters_str
    gait_parameters.draw()

key_height = 60
key_width = 110
def draw_gait():
    glLoadIdentity()
    pyglet.gl.glColor3f(0.0, 1.0, 0.0)
    leftLeg = Leg()
    leftLeg.updateAngles(270 + .2*strain, -20, 100)
    glLoadIdentity()
    pyglet.gl.glColor3f(0.0, 0.0, 1.0)
    rightLeg = Leg()
    rightLeg.updateAngles(270 - .2 * strain, -20, 100)
    glLoadIdentity()
    lbl_gait_title.draw()
    pyglet.gl.glColor3f(1.0, 1.0, 1.0)
    key.blit(vert_line_place + (window_width - vert_line_place)/2 - key_width/2, graph_margin,
             height = key_height, width = key_width)

########## UTIL ##########
LEG_LEN = 150
FOOT_LEN = 50
FIX_X = vert_line_place + (window_width - vert_line_place)/2
FIX_Y = window_height - 100

def segment(x, y, a, l):
    glTranslatef(x, y,0.0)
    glRotatef(float(a),0.0,0.0,1.0)
    draw_segment(0, 0, l, 0)

class Leg:
    def updateAngles(self, hipAngle, kneeAngle, footAngle):
        segment(FIX_X, FIX_Y, hipAngle, LEG_LEN)
        segment(LEG_LEN, 0, kneeAngle, LEG_LEN)
        segment(LEG_LEN, 0, footAngle, FOOT_LEN)

segment_width = 10

def circle(x, y, radius):
    iterations = int(2*radius*pi)
    s = sin(2*pi / iterations)
    c = cos(2*pi / iterations)

    dx, dy = radius, 0

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations+1):
        glVertex2f(x+dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()

def draw_segment(c1x,c1y,c2x,c2y):
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                         ('v2f', [c1x , c1y - segment_width / 2,
                                  c2x , c2y - segment_width / 2,
                                  #c2x + segment_width / 2, c2y,
                                  c2x , c2y + segment_width / 2,
                                  c1x , c1y + segment_width / 2
                                  #c1x - segment_width / 2, c1y
                                  ,]))
    circle(c1x, c1y,segment_width / 2)
    circle(c2x, c2y, segment_width / 2)


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
