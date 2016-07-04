#Author-Tim Booher
#Description-This script draws a circle

import adsk.core, adsk.fusion, traceback
    
#def draw_rectangle(design, x1, y1, x2, y2, d, name):
#    # Get the root component of the active design
#    r = lines.addTwoPointRectangle(adsk.core.Point3D.create(x1, y1, 0), adsk.core.Point3D.create(x2, y2,0))
#    #sketch.profiles.item
#    extInput = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewComponentFeatureOperation)
#    distance = adsk.core.ValueInput.createByReal(d)
#    extInput.setDistanceExtent(False, distance)
#    extInput.name = name
#    k = extrudes.add(extInput)
#    comp = k.parentComponent
#    comp.name = name
    
def draw2(x1, y1, x2, y2, d, name, sketch, lines, extrudes, r):
    oSketchLineList = lines.addTwoPointRectangle(adsk.core.Point3D.create(x1, y1, 0), adsk.core.Point3D.create(x2, y2,0))
    # extrude and make component
    p_index = sketch.profiles.count
    print("working profile %d" % p_index)
    profile = sketch.profiles.item(p_index-1) # r.createOpenProfile(oSketchLineList)
    print("assembly context: %s" % profile.assemblyContext)
    #comp = extrude_comp(profile, d, extrudes)
    #comp.name = name
    
def extrude_comp(profile, d, extrudes):
    # The profile argument can be a single Profile, a single planar face, a single SketchText object, or an ObjectCollection consisting of multiple profiles, planar faces, and sketch texts. When an ObjectCollection is used all of the profiles, faces, and sketch texts must be co-planar.
    extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(d)
    extInput.setDistanceExtent(False, distance)
    extrude = extrudes.add(extInput)
    return extrude.parentComponent

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        design = app.activeProduct

        # Create a new sketch on the xy plane.
        rootComp = design.rootComponent
        xyPlane = rootComp.xYConstructionPlane
        extrudes = rootComp.features.extrudeFeatures
        sketches = rootComp.sketches
        sketch = sketches.add(xyPlane)
        sketch.name = 'back sketch'
        lines = sketch.sketchCurves.sketchLines
        
        # now create some lines
        
        #circles = sketch.sketchCurves.sketchCircles
        # all units in cm
        x = 0
        y = 0
        w = 10
        h = 6
        p = 1
        d = 1
        
        # left
        draw2(x, y+p, x+p, y+h-p, d, 'left', sketch, lines, extrudes, rootComp)
        # right
        draw2(x+w-p, y+p, x+w, y+h-p, d, 'right', sketch, lines, extrudes, rootComp)
        # top
        draw2(x, y+h-p, x+w, y+h, d, 'top', sketch, lines, extrudes, rootComp)
        # bottom
        draw2(x, y, x+w, y+p, d, 'bottom', sketch, lines, extrudes, rootComp)
        # back
        draw2(x, y, x+w, y+h, -d, 'back', sketch, lines, extrudes, rootComp)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
