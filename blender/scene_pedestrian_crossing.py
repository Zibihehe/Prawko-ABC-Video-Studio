import bpy, math

FPS = 24
DURATION = 30
END_FRAME = FPS * DURATION

# ---------- helpers ----------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def set_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 8
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 75
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = END_FRAME
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = __import__('os').path.abspath('render_frames/frame_')


def mat(name, color, rough=0.5, metallic=0.0, emission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission Strength'].default_value = emission
        bsdf.inputs.get('Emission Color', bsdf.inputs.get('Emission')).default_value = (*color, 1.0)
    return m


def apply(obj, material):
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def cube(name, loc, scale, material=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if material:
        apply(obj, material)
    return obj


def plane(name, loc, scale, rot=(0,0,0), material=None):
    bpy.ops.mesh.primitive_plane_add(location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if material:
        apply(obj, material)
    return obj


def cylinder(name, loc, radius, depth, material=None):
    bpy.ops.mesh.primitive_cylinder_add(location=loc, radius=radius, depth=depth)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        apply(obj, material)
    return obj


clear_scene()
set_render()
scene = bpy.context.scene

# ---------- materials ----------
road_mat = mat('Road', (0.10, 0.10, 0.12), rough=0.9)
line_mat = mat('Line', (0.95, 0.95, 0.92), rough=0.7)
grass_mat = mat('Grass', (0.11, 0.35, 0.10), rough=1.0)
sidewalk_mat = mat('Sidewalk', (0.62, 0.62, 0.62), rough=1.0)
building_mat = mat('Building', (0.65, 0.66, 0.67), rough=1.0)
window_mat = mat('Window', (0.45, 0.70, 0.95), rough=0.1, metallic=0.1, emission=0.1)
sign_blue = mat('SignBlue', (0.04, 0.22, 0.80), rough=0.4)
pole_mat = mat('Pole', (0.4, 0.4, 0.42), rough=0.7)
car_blue = mat('CarBlue', (0.05, 0.22, 0.75), rough=0.35, metallic=0.1)
car_dark = mat('CarDark', (0.05, 0.05, 0.06), rough=0.8)
ped_body = mat('PedBody', (0.08, 0.12, 0.45), rough=0.8)
ped_skin = mat('PedSkin', (0.85, 0.72, 0.60), rough=0.7)
white_mat = mat('White', (1,1,1), rough=0.5)
red_mat = mat('Red', (0.65,0.02,0.02), rough=0.4)

# ---------- world ----------
world = scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.62, 0.82, 1.0, 1.0)
bg.inputs[1].default_value = 0.9

# lighting
bpy.ops.object.light_add(type='SUN', location=(0,0,10))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(50), math.radians(0), math.radians(25))
sun.data.energy = 3.2

bpy.ops.object.light_add(type='AREA', location=(0, -10, 8))
fill = bpy.context.active_object
fill.rotation_euler = (math.radians(70), 0, 0)
fill.data.energy = 1500
fill.data.size = 10

# ---------- environment ----------
plane('Ground', (0, 0, 0), (80, 80, 1), material=grass_mat)
plane('Road', (0, 25, 0.01), (3.5, 30, 1), material=road_mat)
plane('LeftWalk', (-4.4, 25, 0.02), (0.9, 30, 1), material=sidewalk_mat)
plane('RightWalk', (4.4, 25, 0.02), (0.9, 30, 1), material=sidewalk_mat)

# center lane dashes
for i in range(10):
    if not 15 < 4+i*5.5 < 22:
        plane(f'Dash_{i}', (0, 4+i*5.5, 0.03), (0.06, 1.0, 1), material=line_mat)

# zebra crossing stripes
zebra_y = 17.0
for i in range(12):
    plane(f'Zebra_{i}', (-3.025+i*0.55, zebra_y+1.5, 0.03), (0.21, 1.5, 1), material=line_mat)

# buildings
coords = [(-10,10), (-12,21), (-9,33), (10,12), (12,25), (9,36)]
for idx, (x,y) in enumerate(coords):
    w = 1.8 + (idx % 2) * 0.5
    d = 1.8 + ((idx+1) % 2) * 0.7
    h = 2.8 + (idx % 3) * 1.2
    b = cube(f'Building_{idx}', (x, y, h), (w, d, h), building_mat)
    # front windows
    for floor in range(1, int(h*1.5)):
        for col in (-0.8, 0, 0.8):
            bpy.ops.mesh.primitive_plane_add(location=(x+col, y-d-0.01, floor*0.9))
            win = bpy.context.active_object
            win.scale = (0.22, 0.28, 1)
            win.rotation_euler = (math.radians(90), 0, 0)
            apply(win, window_mat)

# sign on right
pole = cylinder('SignPole', (5.1, 18.5, 1.4), 0.05, 2.8, pole_mat)
sign = cube('Sign', (5.1, 18.5, 3.0), (0.55, 0.05, 0.55), sign_blue)
# D-6 pictogram on the forward-facing surface
def signpoly(name, coords, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(5.1+x,18.445,3+z) for x,z in coords], [], [tuple(range(len(coords)))])
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)
signpoly('White triangle',[(-.43,-.36),(.43,-.36),(0,.44)],white_mat)
def symbol(name,coords):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(5.1+x,18.44,3+z) for x,z in coords],[],[tuple(range(len(coords)))])
    mesh.update()
    obj=bpy.data.objects.new(name,mesh); scene.collection.objects.link(obj); obj.data.materials.append(car_dark)
symbol('Walking torso',[(-.04,.15),(.05,.15),(.07,-.09),(-.03,-.09)])
symbol('Head',[ (.01+.045*math.cos(i*math.pi/8),.22+.045*math.sin(i*math.pi/8)) for i in range(16)])
symbol('Arm',[(-.04,.13),(-.19,-.02),(-.16,-.06),(.02,.07),(.18,-.04),(.20,0),(.05,.15)])
symbol('Legs',[(-.03,-.07),(-.19,-.28),(-.12,-.28),(.025,-.15),(.15,-.28),(.22,-.28),(.07,-.07)])
for i in range(5):
    x=-.28+i*.115
    symbol('Crosswalk stripe',[(x,-.31),(x+.07,-.31),(x+.07,-.35),(x,-.35)])

# simple car hood at bottom foreground
hood = cube('CarHood', (0, 2.2, 0.55), (2.2, 1.8, 0.35), car_blue)
windshield = cube('WindshieldBase', (0, 3.7, 1.1), (1.6, 0.12, 0.8), car_dark)

# pedestrian rig (simple objects parented to empty)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
ped = bpy.context.active_object
ped.name = 'Pedestrian'
head = bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 1.65), radius=0.18)
head_obj = bpy.context.active_object; apply(head_obj, ped_skin); head_obj.parent = ped
body = cube('PedBody', (0, 0, 1.05), (0.18, 0.11, 0.42), ped_body); body.parent = ped
leg1 = cube('Leg1', (.10, 0, .45), (0.06, 0.05, 0.42), car_dark); leg1.parent = ped
leg2 = cube('Leg2', (-.10, 0, .45), (0.06, 0.05, 0.42), car_dark); leg2.parent = ped
arm1 = cube('Arm1', (.20, 0, 1.05), (0.05, 0.05, 0.28), ped_body); arm1.parent = ped
arm2 = cube('Arm2', (-.20, 0, 1.05), (0.05, 0.05, 0.28), ped_body); arm2.parent = ped

# keyframe pedestrian crossing
ped.location = (-4.1, zebra_y+1.6, 0)
ped.keyframe_insert(data_path='location', frame=1)
ped.location = (-4.1, zebra_y+1.6, 0)
ped.keyframe_insert(data_path='location', frame=FPS*7)
ped.location = (4.1, zebra_y+1.6, 0)
ped.keyframe_insert(data_path='location', frame=FPS*16)
ped.location = (4.1, zebra_y+1.6, 0)
ped.keyframe_insert(data_path='location', frame=END_FRAME)

# walking swing
for frame in range(1, END_FRAME+1, 8):
    phase = math.sin(frame/5) if FPS*7 < frame < FPS*16 else 0
    leg1.rotation_euler = (phase*0.35, 0, 0)
    leg2.rotation_euler = (-phase*0.35, 0, 0)
    arm1.rotation_euler = (-phase*0.35, 0, 0)
    arm2.rotation_euler = (phase*0.35, 0, 0)
    for obj in (leg1, leg2, arm1, arm2):
        obj.keyframe_insert(data_path='rotation_euler', frame=frame)

# camera
bpy.ops.object.camera_add(location=(0, 2.8, 1.55), rotation=(math.radians(85), 0, 0))
cam = bpy.context.active_object
cam.data.lens = 30
scene.camera = cam

# animate car/camera motion: approach crossing, stop, then move again
positions = [
    (1, 2.8),
    (FPS*6, 12.0),
    (FPS*7, 12.0),
    (FPS*18, 12.0),
    (END_FRAME, 32.0),
]
for frame, y in positions:
    cam.location = (1.45, y, 1.55)
    cam.keyframe_insert(data_path='location', frame=frame)
    hood.location = (1.8, y+1.2, 0.55)
    hood.scale = (.85, 1.1, .25)
    hood.keyframe_insert(data_path='location', frame=frame)
    windshield.location = (1.8, y+0.55, .40)
    windshield.scale = (.85,.20,.15)
    windshield.keyframe_insert(data_path='location', frame=frame)

# slight focus object near crossing
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, zebra_y+2.2, 1.2))
focus = bpy.context.active_object
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus
cam.data.dof.aperture_fstop = 6.5

# Save scene; explicit frame loop is controlled by workflow.
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=__import__('os').path.abspath('rendered/scene.blend'))
print('Scene generated successfully')
