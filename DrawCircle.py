#Author-Tim Booher
#Description-This script draws a circle

import adsk.core, adsk.fusion, traceback
#import math

# todo:
# - get objects to extract correctly
# - place tabs
# - place shelves
# - combine objects
# - dogbone
# - yeah
cm = 2.54
circle_radius = (1/8)*cm

#// Create a transform to do move

def createNewComponent(rootComp):
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component
    
def draw2(x1, y1, x2, y2, name, sketch, lines, parent_component = []):
    # returns SketchLineList
    lines.addTwoPointRectangle(adsk.core.Point3D.create(x1, y1, 0), adsk.core.Point3D.create(x2, y2,0)) 
    
def extrude_all(sketch, d, parent_component):
    for profile in sketch.profiles:
        extrude_comp(profile, d, parent_component, sketch.name)
    
def extrude_comp(profile, d, parent, name):
    # The profile argument can be a single Profile, a single planar face, a single SketchText object, or an ObjectCollection consisting of multiple profiles, planar faces, and sketch texts. When an ObjectCollection is used all of the profiles, faces, and sketch texts must be co-planar.
    extrudes = parent.features.extrudeFeatures
    extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(d)
    extInput.setDistanceExtent(False, distance)
    extrude = extrudes.add(extInput)
    comp = extrude.parentComponent
    if (name == 'shelves') and False: # not working yet
        move_component(comp, parent)
    comp.name = name
    
def move_component(e, parent):
    # doesn't work
    try:
        ents = adsk.core.ObjectCollection.create()
        print("working on %s" % e.bRepBodies.item(0).name)
        ents.add(e.bRepBodies.item(0))
        
        # translation
        #vector = adsk.core.Vector3D.create(0.0, 100.0, 0.0)
        vector =  adsk.core.Vector3D.create(0.0, 10.0, 0.0)
        transform = adsk.core.Matrix3D.create()
        transform.translation = vector
        
        # Create a move feature
        features = parent.features
        moveFeats = features.moveFeatures
        moveFeatureInput = moveFeats.createInput(ents, transform)
        moveFeats.add(moveFeatureInput)
        
    except: 
        print('Move Failed: {}'.format(traceback.format_exc()))
        pass#Check if there is unexpected, but should handle case where there is no needed movement
    
def draw_tabs(x,y,w,h,p, sketch, lines, n, comp):
    # calculate number of shelves
    a = (h - p*(2+n))/(n+1) # tab width
    c = 1/3
    for i in range(1,n+2):
        y_base = (y + i*(p+a))
        y_start = y_base-a*(1-c) 
        y_end   = y_base-a*c
        draw2(x, y_start, x+w, y_end, "shelf %d" % i, sketch, lines, comp)
        
def draw_horizontal_tabs(x,y,w,h,p, sketch, lines, comp):
    tabs = 11.0
    tab_width =w/tabs
    # error if tab_width
    print("the width %d" % tab_width)
    print("we have %d tabs with width: %d" % (tabs, tab_width))
    for j in range(0,int(tabs)):
        if j % 2 != 0:
            draw2(x+j*tab_width, y, x+tab_width*(j+1), y + h, "tab %d" % j, sketch, lines, comp)
    
def create_sketch(name, plane, sketches):
    sketch = sketches.add(plane)
    sketch.name = name
    lines = sketch.sketchCurves.sketchLines
    return sketch, lines
    
def draw_shelves(x,y,w,h,p, sketch, lines, n, parent):
    # calculate number of shelves
    a = (h - p*(2+n))/(n+1)
    hp = p/2
    for i in range(1,n+1):
        y_start = y + i*(p+a) 
        y_end   = y_start + p
        draw2(x+hp, y_start, x+w-hp, y_end, "shelf %d" % i, sketch, lines, parent)
        
def draw_circles(start_x, end_x, y, n, h, p, num_circles, sketch):
    # calculate number of shelves
    a = (h - p*(2+n))/(n+1)
    for i in range(1,n+1):
        y_start = y + i*(p+a) 
        y_end   = y_start + p
        y0 = (y_start+y_end)/2
        circles = sketch.sketchCurves.sketchCircles
        for x in [start_x + float(x)/(num_circles-1)*(end_x-start_x) for x in range(num_circles)]:
            circles.addByCenterRadius(adsk.core.Point3D.create(x, y0, 0), circle_radius)
        
def set_param(name, value, units, comment, design):
    value_input = adsk.core.ValueInput.createByReal(float(value))
    design.userParameters.add(name, value_input, units, comment)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        design = app.activeProduct

        # Create a new sketch on the xy plane.
        rootComp = design.rootComponent
        xyPlane = rootComp.xYConstructionPlane
        sketches = rootComp.sketches
        comp = createNewComponent(rootComp)
        comp.name = 'shelf'
        
        # all units in cm
        inputs = {}
        inputs['x'] = 0
        inputs['y'] = 0
        inputs['w'] = 46.0*cm
        inputs['h'] = 8*12*cm
        inputs['p'] = 0.706*cm
        inputs['d'] = 10*cm
        inputs['shelves'] = 8
               
        for key, value in inputs.items():
            set_param(key, value, 'in', 'set by code', design)

        x = inputs['x']
        y = inputs['y']
        w = inputs['w']
        h = inputs['h']
        p = inputs['p']
        d = inputs['d']
        
        shelves = inputs['shelves']
        
        print("your shelf height will be %d in" % ((h/shelves-p)/2.5))
        
        sketch, lines = create_sketch('left and right', xyPlane, sketches)
        # left
        draw2(x, y+p/2, x+p, y+h-p/2, 'left', sketch, lines, comp)
        # right
        draw2(x+w-p, y+p/2, x+w, y+h-p/2, 'right', sketch, lines, comp)
        extrude_all(sketch, d - p/2, comp)
        
        sketch, lines = create_sketch('top_and_bottom', xyPlane, sketches)
        # top
        draw2(x, y+h-p, x+w, y+h, 'top', sketch, lines, comp)
        # bottom
        draw2(x, y, x+w, y+p, 'bottom', sketch, lines, comp)
        extrude_all(sketch, d - p/2, comp)
        
        sketch, lines = create_sketch('back', xyPlane, sketches)
        # back
        draw2(x, y, x+w, y+h, 'back', sketch, lines, comp)
        extrude_all(sketch, p, comp)
                
        shelves_comp = createNewComponent(comp)
        shelves_comp.name = 'shelves'      
        sketch, lines = create_sketch('shelves', xyPlane, sketches)
        draw_shelves(x,y,w,h,p, sketch, lines, shelves, shelves_comp)
        extrude_all(sketch, d - p/2, shelves_comp)
        
        circles_comp = createNewComponent(comp)
        circles_comp.name = 'holes'
        hole_sketch, lines = create_sketch('holes', xyPlane, sketches)
        o = 2*cm
        draw_circles(x+p+o, x+w-p-o, y, shelves, h, p, 4, hole_sketch)
        
        extrude_all(hole_sketch, p, circles_comp)
        
        if False:
            horz_tabs = createNewComponent(comp)
            horz_tabs.name = 'horz tabs'
            sketch, lines = create_sketch('horz tabs', xyPlane, sketches)
            draw_tabs(x,y,w,h,p, sketch, lines, shelves, horz_tabs)
            extrude_all(sketch, p, horz_tabs)
            
            vert_tabs = createNewComponent(comp)
            vert_tabs.name = 'vert tabs'
            sketch, lines = create_sketch('vert tabs', xyPlane, sketches)
            draw_horizontal_tabs(x,y,w,h,p,sketch,lines,vert_tabs)
            extrude_all(sketch, p, vert_tabs)        
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
