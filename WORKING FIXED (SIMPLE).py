# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 09:35:25 2024

@author: mrblu
"""

import os
from pathlib import Path
from bifacial_radiance import RadianceObj

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_11'

# Another option using relative address; for some operative systems you might need '/' instead of '\'
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')

print ("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

try:
   from bifacial_radiance import *
except ImportError:
   raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np
import pandas as pd

hub_height = 5.5

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
tilts =[25, 35, 45, 55, 65, 75] # tilt.

for jj in range (0, len(tilts)):
    tilt = tilts[jj]
    simulationname = 'AgriPV'+ str(int(tilt))+"deg"
    

    demo = RadianceObj(simulationname,path = testfolder)
    demo.setGround(albedo)
    epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057
    metdata = demo.readWeatherFile(epwfile, coerce_year=2001)
    timestamp = metdata.datetime.index(pd.to_datetime('2001-06-17 13:0:0 -5'))  # Make this timezone aware, use -5 for EST.
    demo.gendaylit(timestamp)

    
    module_type = 'test-module'
    module = demo.makeModule(name=module_type,x=1.695, y=0.984)
    print(module)

    availableModules = demo.printModules()

    sceneDict = {'tilt':tilt,'pitch': 15,'hub_height':hub_height,'azimuth':azimuth_ang, 'nMods': nMods, 'nRows': nRows}


    scene = demo.makeScene(module=moduletype,sceneDict=sceneDict)


    octfile = demo.makeOct(demo.getfilelist())
    
    #!rvu -vf views\front.vp -e .01 AgriPV650cm.oct

    demo.getfilelist()

    analysis = AnalysisObj(octfile, demo.basename)
    sensorsy = 5
    modWanted = 1
    rowWanted = 2
    frontscan, backscan = analysis.moduleAnalysis(scene, modWanted=modWanted, rowWanted=rowWanted, sensorsy=sensorsy)

    analysis.analysis(octfile, simulationname, frontscan, backscan)

