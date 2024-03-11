# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 09:43:41 2024

@author: mrblu
"""

import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' /  'Tutorial_11')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

print ("Your simulation will be stored in %s" % testfolder)

from bifacial_radiance import *
import numpy as np
import pandas as pd

hub_heights = [6.5, 5.5, 4.5, 3.5, 2.5, 1.5]

simulationname = 'AgriPV'

#Location:
lat = 40.0583  # NJ
lon = -74.4057  # NJ

# MakeModule Parameters
moduletype='test-module'
numpanels = 3  # AgriPV site has 3 modules along the y direction (N-S since we are facing it to the south) .
x = 0.95
y = 1.95
xgap = 2.0# Leaving 15 centimeters between modules on x direction
ygap = 0.005 # Leaving 10 centimeters between modules on y direction
zgap = 0 # no gap to torquetube.
sensorsy = 6*numpanels  # this will give 6 sensors per module, 1 per cell

# Other default values:

# TorqueTube Parameters
axisofrotationTorqueTube=False  # this is False by default if there is no torquetbue parameters
torqueTube = False
cellLevelModule = True

numcellsx = 12
numcellsy = 6
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02

cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy,
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}

# SceneDict Parameters
pitch = 15 # m
albedo = 0.2  #'grass'     # ground albedo
nMods = 5 # 5 modules per row.
nRows = 3  # 3 row

azimuth_ang=180 # Facing south
tilt =35 # tilt.

for jj in range (0, len(hub_heights)):
    hub_height = hub_heights[jj]
    simulationname = 'AgriPV'+ str(int(hub_height*100))+'cm'
    
    torquetube_height = hub_height - 0.1 # m

# Now let's run the example

    demo = RadianceObj(simulationname,path = testfolder)
    demo.setGround(albedo)
    epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057
    metdata = demo.readWeatherFile(epwfile, coerce_year=2001)
    timestamp = metdata.datetime.index(pd.to_datetime('2001-06-17 13:0:0 -5'))  # Make this timezone aware, use -5 for EST.
    demo.gendaylit(timestamp)


# Making module with all the variables
    module=demo.makeModule(name=moduletype,x=x,y=y,numpanels=numpanels,
                           xgap=xgap, ygap=ygap, cellModule=cellLevelModuleParams)
# create a scene with all the variables
    sceneDict = {'tilt':tilt,'pitch': 15,'hub_height':hub_height,'azimuth':azimuth_ang, 'nMods': nMods, 'nRows': nRows}
    scene = demo.makeScene(module=moduletype, sceneDict=sceneDict)
    octfile = demo.makeOct(demo.getfilelist())


    torquetubelength = module.scenex*(nMods)

    name='Post1'
    text='! genbox Metal_Aluminum_Anodized torquetube_row1 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 0 4.2'.format(
                                                    torquetubelength, (-torquetubelength+module.sceney)/2.0)
    customObject = demo.makeCustomObject(name,text)
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")

    name='Post2'
    text='! genbox Metal_Aluminum_Anodized torquetube_row2 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 15 4.2'.format(
                                            torquetubelength, (-torquetubelength+module.sceney)/2.0)
    customObject = demo.makeCustomObject(name,text)
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")

    name='Post3'
    text='! genbox Metal_Aluminum_Anodized torquetube_row2 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 -15 4.2'.format(
                                              torquetubelength, (-torquetubelength+module.sceney)/2.0)
    customObject = demo.makeCustomObject(name,text)
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")

    name='Pile'
    pile1x = (torquetubelength+module.sceney)/2.0
    pilesep = pile1x*2.0/7.0

    text= '! genrev Metal_Grey tube1row1 t*4.2 0.15 32 | xform -t {} 0 0'.format(pile1x)
    text += '\r\n! genrev Metal_Grey tube1row2 t*4.2 0.15 32 | xform -t {} 15 0'.format(pile1x)
    text += '\r\n! genrev Metal_Grey tube1row3 t*4.2 0.15 32 | xform -t {} -15 0'.format(pile1x)

    for i in range (1, 7):
        text += '\r\n! genrev Metal_Grey tube{}row1 t*4.2 0.15 32 | xform -t {} 0 0'.format(i+1, pile1x-pilesep*i)
        text += '\r\n! genrev Metal_Grey tube{}row2 t*4.2 0.15 32 | xform -t {} 15 0'.format(i+1, pile1x-pilesep*i)
        text += '\r\n! genrev Metal_Grey tube{}row3 t*4.2 0.15 32 | xform -t {} -15 0'.format(i+1, pile1x-pilesep*i)

    customObject = demo.makeCustomObject(name,text)
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")

    octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object files we just added into a .oct file

    !rvu -vf views\front.vp -e .01 AgriPV650cm.oct

    analysis = AnalysisObj(octfile, demo.name)
    sensorsy = 5
    modWanted = 1
    rowWanted = 2
    frontscan, backscan = analysis.moduleAnalysis(scene, modWanted=modWanted, rowWanted=rowWanted, sensorsy=sensorsy)


    analysis.analysis(octfile, simulationname, frontscan, backscan)  # compare the back vs front irradiance

