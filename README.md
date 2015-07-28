The **'Angry birds' optimisation** project demonstrates modeling and optimizing throw of body, determined by user.

**Problem description**   
In general, the design problem is to choose such start parameters of throw that provide the best values of score (representation od damage caused by throw).   
Objective to be minimized: start kinetic energy.   
Since the function of distance is complex and not analitic it is important to enable global optimisation be setting GlobalPhaseIntensity - parameter of block "Optimizer0".   
There are three parameters that could be varied during optimization: <lin\_velocity\_amplitude>, <lin\_velocity\_angle>, <angular\_velocity>.   

Example contains three workflows:   
The [ThreeParametersVaried](./ThreeParametersVaries.p7wf) workflow use three parameters (linear velocity, angle and angular velocity) to optimize model.   

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
6) <material\_type> is name of material described in section <materials>
7) <is\_projectile> field which should be set to _True_ in case this body is projectile
8) body can consist of severals shapes which whould be treated as one, so every shape should be described in section <shape>
8.1) shape could be <circle>, <rectangle> and <polygon>.
8.1.1) <circle> shape is decribed by local position <position> and radius <radius>
8.1.2) <rectangle> shape is decribed by width <width> and height <height>
8.1.3) <polygon> shape is decribed as a array of points <point>

     


Projectile is described as a body.

Ground settings:
Ground is a number of connected edges   
Edge ends' coordinates are set in section <vertices>   
Two nearby vertices describe one edge   
Vertices are global   

Modelling settings:   
1) there are two conditions (sign) to stop modelling:   
   1.1) first is Body is stopped
        (body is consider to be stopped when it's linear velocity is below <epsilon\_lin\_velocity>)
   1.2) second is Body's center of mass is out of modelling field      
        (modelling field is all space between leftmost point and rightmost point and above the bottom of ground)   
2) also it possible to change gravity constant be setting field <g>,   
3) other settings (<velocity\_iterations>, <position\_iterations>, <hz>) are settings of box2d modelling engine   
   (It's higly recommended **not** to change them).   

**Simulation**   
Modelling is performed by python script model.py which use framework pybox2d for simulation world.   

Result of modelling is xml file OUTPUT.dat which contains points of trajectory in section <field> and additional information in section <result>   
Additional information, which is mentioned there is:   
1) final distance between target and body at the last step - <distance>   
   (distance between body and target is distance between target point and the closet body point),   
2) minimal distance between body and target which was achivied while body was moving - <min\_distance>,   
3) body mass - <mass>.   
4) body inertia - <inertia>.   
5) body state which is describe by all vertices of body - <body>.   

Additional output is png image of throw trajectory with result distance printed in it.   
This image is located in directory out (relativle from the location of python script)   
![](./doc/img/img0.png)

