# ================== NavIC Trajectory (Colored Segments) + Drone Follow ==================
# Blender 4.x safe, no deletion of your objects.

import bpy
import math
import random

# --------- User Params ----------
fs_trajectory = 100        # samples/sec
total_time    = 60.0       # seconds
R             = 50.0       # radius (Blender units)
t1, t2        = 20.0, 40.0 # jamming window (for colouring)
navic_std     = 1.2        # small noise like NavIC
bevel_depth   = 0.08       # visible line thickness
path_duration = 600        # animation frames
drone_name_preference = "Drone"  # try this name first
# Colors (RGBA 0..1)
COL_NONJAM  = (0.00, 0.60, 0.00, 1.0)  # green
COL_RAMPUP  = (1.00, 0.75, 0.00, 1.0)  # yellow/orange
COL_FULLJAM = (1.00, 0.00, 0.00, 1.0)  # red
COL_RAMPDN  = (1.00, 0.40, 0.20, 1.0)  # orange-red
# ---------------------------------

# ---------- helpers ----------
def make_emission_mat(name, rgba, strength=4.0):
    """simple Emission material (stable in 4.x)"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em  = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mat.diffuse_color = rgba
    return mat

def pick_drone_object():
    obj = bpy.data.objects.get(drone_name_preference)
    if obj and obj.type in {"MESH","EMPTY","ARMATURE"}: return obj
    obj = bpy.context.view_layer.objects.active
    if obj and obj.type in {"MESH","EMPTY","ARMATURE"}: return obj
    for ob in bpy.data.objects:
        if ob.type in {"MESH","EMPTY","ARMATURE"}: return ob
    return None

def add_poly_curve(name, pts_xyz, material=None, bevel=0.0):
    """Create a poly curve from list of (x,y,z)."""
    cu = bpy.data.curves.new(name, type='CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 1
    if bevel > 0.0:
        cu.bevel_depth = bevel
        cu.bevel_resolution = 2

    sp = cu.splines.new(type='POLY')
    sp.points.add(len(pts_xyz)-1)
    for i,(x,y,z) in enumerate(pts_xyz):
        sp.points[i].co = (x, y, z, 1.0)

    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)

    if material:
        if material.name not in [m.name for m in cu.materials]:
            cu.materials.append(material)
        sp.material_index = cu.materials.find(material.name)

    return obj
# -------------------------------

# --------- 1) Generate trajectory like MATLAB (NavIC track) ---------
dt = 1.0 / fs_trajectory
N  = int(total_time / dt)
t  = [i*dt for i in range(N)]

omega = 2.0*math.pi/total_time
def x_true(tt): return R*math.cos(omega*tt)
def y_true(tt): return R*math.sin(omega*tt)

# NavIC: small noise, no jamming boost
x_nav = [x_true(tt) + random.gauss(0.0, navic_std) for tt in t]
y_nav = [y_true(tt) + random.gauss(0.0, navic_std) for tt in t]

# Downsample exactly like your MATLAB (fs_trajectory/2)
fs_ds = fs_trajectory // 2
idx_ds = list(range(0, N, fs_ds))
t_ds   = [t[i] for i in idx_ds]
x_ds   = [x_nav[i] for i in idx_ds]
y_ds   = [y_nav[i] for i in idx_ds]
z_ds   = [0.0 for _ in idx_ds]

# Segment boundaries on t_ds
def first_idx_geq(arr, val):
    for i,v in enumerate(arr):
        if v >= val: return i
    return len(arr)-1
i_ru_s = first_idx_geq(t_ds, 20.0)
i_ru_e = first_idx_geq(t_ds, 24.0)
i_fj_e = first_idx_geq(t_ds, 36.0)
i_rd_e = first_idx_geq(t_ds, 40.0)

seg_ranges = [
    (0,        i_ru_s, COL_NONJAM,  "NonJam_A"),
    (i_ru_s,   i_ru_e, COL_RAMPUP,  "RampUp"),
    (i_ru_e,   i_fj_e, COL_FULLJAM, "FullJam"),
    (i_fj_e,   i_rd_e, COL_RAMPDN,  "RampDown"),
    (i_rd_e,   len(t_ds), COL_NONJAM, "NonJam_B"),
]

# --------- 2) Make one invisible FOLLOW curve (single spline) ---------
follow_pts = list(zip(x_ds, y_ds, z_ds))
follow_curve = add_poly_curve("NavIC_Path_FOLLOW", follow_pts, None, bevel=0.0)
follow_curve.data.use_path = True
follow_curve.hide_render = True
follow_curve.hide_viewport = True   # invisible guide

# --------- 3) Make COLOR display segments (5 separate curves) ---------
mat_nonjam  = make_emission_mat("NonJammed_MAT",  COL_NONJAM)
mat_rampup  = make_emission_mat("RampUp_MAT",     COL_RAMPUP)
mat_fulljam = make_emission_mat("FullJam_MAT",    COL_FULLJAM)
mat_rampdn  = make_emission_mat("RampDown_MAT",   COL_RAMPDN)

mat_map = {
    "NonJam_A": mat_nonjam,
    "RampUp":   mat_rampup,
    "FullJam":  mat_fulljam,
    "RampDown": mat_rampdn,
    "NonJam_B": mat_nonjam,
}

for a,b,_,label in seg_ranges:
    if b-a < 2: 
        continue
    pts = [(x_ds[i], y_ds[i], z_ds[i]) for i in range(a, b)]
    add_poly_curve(f"Seg_{label}", pts, mat_map[label], bevel=bevel_depth)

# --------- 4) Attach your drone to the follow curve ---------
drone = pick_drone_object()
if drone is None:
    print("⚠️ Drone object not found. Rename your drone to 'Drone' or select it before running.")
else:
    # remove old follow-path constraints
    for c in list(drone.constraints):
        if c.type == 'FOLLOW_PATH':
            drone.constraints.remove(c)

    con = drone.constraints.new(type='FOLLOW_PATH')
    con.target = follow_curve
    con.use_fixed_location = True
    con.forward_axis = 'FORWARD_Y'
    con.up_axis = 'UP_Z'

    # Animate path duration
    follow_curve.data.path_duration = path_duration
    # try auto animate
    try:
        bpy.ops.object.select_all(action='DESELECT')
        follow_curve.select_set(True)
        bpy.context.view_layer.objects.active = follow_curve
        bpy.ops.object.constraint_followpath_path_animate(constraint=con.name)
    except Exception:
        # manual fallback
        follow_curve.data.eval_time = 0.0
        follow_curve.data.keyframe_insert(data_path="eval_time", frame=1)
        follow_curve.data.eval_time = path_duration
        follow_curve.data.keyframe_insert(data_path="eval_time", frame=path_duration)

    print("✅ Drone attached. Duration:", path_duration, "frames")

print("✅ Colored NavIC-style path created (Green → Yellow → Red → Orange → Green).")
# =====================================================================