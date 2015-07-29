The **'Angry birds' optimisation** project demonstrates modeling and optimizing throw of body, determined by user.

**Problem description**   
In general, the design problem is to choose such start parameters of throw that provide the best values of score (representation od damage caused by throw).   
Objective to be minimized: start kinetic energy.   
Since the function of distance is complex and not analitic it is important to enable global optimisation be setting GlobalPhaseIntensity - parameter of block "Optimizer0".   
There are three parameters that could be varied during optimization: <lin\_velocity\_amplitude>, <lin\_velocity\_angle>, <angular\_velocity>.   

Example contains three workflows:   
The [ThreeParametersVaried](./ThreeParametersVaries.p7wf) workflow uses three parameters (linear velocity, angle and angular velocity) to optimize model.   

**Note:** project require python2.7, pybox2d (version '2.3b0') and Bokeh (0.9.1) installed.

**Settings**   
XML-file describing settings is used as an input.

Projectile's, ground's, materials', world's and some model's parameters are set in xml document INPUT.dat in the relevant section <projectile>, <ground>, <materials>,  <blocks> and <model>.   

All sizes should be set accordingly with SI.   

Body settings:
1) geometry is polygon which is described by local vertices (more than 3) in the section <geometry>,   
2) start linear velocity amplitude is set by field <lin\_velocity\_amplitude>,   
3) start linear velocity angle is set by field <lin\_velocity\_angle>,   
4) start angular velocity is set by field <angular\_velocity>,   
5) start position is decribed in section <position>
   (if this body is described in block than position set locally, else globally),   
6) <material\_type> is name of material described in section <materials>,   
7) <is\_projectile> field which should be set to _True_ in case this body is projectile,   
8) body can consist of severals shapes which whould be treated as one, so every shape should be described in section <shapes>.   
8.1) shape could be <circle>, <rectangle> and <polygon>:   
8.1.1) <circle> shape is decribed by local position <position> and radius <radius>;   
8.1.2) <rectangle> shape is decribed by width <width> and height <height>;   
8.1.3) <polygon> shape is decribed as an array of points <point>;  


Projectile is described as a body.   

Ground settings:
Ground is a number of connected edges   
Edge ends' coordinates are set in section <vertices>   
Two nearby vertices describe one edge   
Vertices are global   

Modelling settings:   
1) condition (sign) to stop modelling:   
   each body has stopped
        (body is consider to be stopped when it's linear velocity is below <epsilon\_lin\_velocity>)
   or it's center of mass is out of modelling field      
        (modelling field is all space between leftmost point and rightmost point and above the bottom of ground)   
2) also it possible to change gravity constant be setting field <g>,   
3) other settings (<velocity\_iterations>, <position\_iterations>, <hz>) are settings of box2d modelling engine   
   (It's higly recommended **not** to change them).   

World describe as a number of blocks each of them should be described in section <blocks>.   
Each block has it's global position and some number og bodies.   
With such entity as block it is easy to create to simillar constructions with bodies but in different places: you should copy block <bodies> and than change position by changing section
<position> of block.      
Also it will help you to easily move construction while designing world: the only thing you should do is change block's position
every body in block is describe as entity <body> in block's section <bodies>

**Simulation**   
Modelling is performed by python script model.py which use framework pybox2d for simulation world.   

There are several settings which are provided as command line arguments.  
They are:
1) for testing while developping '-v'/'--visualized' 
   **NOTE**
   It requiers additional pybox2d testing scripts (https://github.com/pybox2d/pybox2d/tree/master/examples):
    - pygame\_framework.py
    - framework.py
    - settings.py
   using this key model.py script will simulate it visually with the tools of pybox2d
2) '-sh'/'--show' - by using this key python script will show html file in new tab in browser (note: using this key will enable saving if the key --nosave are used)       
3) '-ns'/'--nosave' - this key disable saving and creating of html file (this key is quite useful in optimization process ass you probably are not interested in html file)
   **NOTE** keys bellow do not matter if you are using -ns
4) '-l number'/'--limit number' - it will set the limit for an amount of iteration which will be shown in html file (file's size larger as the number higher)
   default value: 201 (it will show 200 iterations + zero iteration with start world state)   
5) '-sz number'/'--size number' - thiw key will set the limit for the maximum between width and height of the picture on html file (however it is also possible to change it in browser)   
   default value: 1200

For instance:
   "python model.py -ns"   
   It will run simulation without creating and saving html file.   
   "python model.py -l 151 -sz 900"   
   It will run simulation with creating and saving html file with limitted anount of iterations displyed to 151 and adjusting picture to 900 pixels.   
   "python model.py -sh"   
   It will run simulation with creating and saving html file and showing it in new tab of browser (be careful it could raise a error and though it is not dangerous it will stop workflow).   

Result of modelling (stored in directory 'out/'):   
1) xml file OUTPUT.dat which contains the result state of the world is section <blocks> (it represented in such way that it is possible to rerun script using the result
    state of the world) and score in section <score>   
2) html file which shows the simulation     

Workflow provides the output of optimal simulation in sandbox 'simulation/'   
It also provides additional output: INPUT.dat which matches the optimul settings (it also placed in directory 'out/')   
