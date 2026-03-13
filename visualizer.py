from sajilopygame import *

# instantiating the class
visualizer = sajilopygame(wwidth=1350, wheight=750)

# title of the window
visualizer.window_title("Odometry Visualizer")

# robot character
robot = visualizer.character(parent=visualizer,type="shape",character_shape="rectangle",
                             color=(0,0,255),org=(0,visualizer.wheight-40),width=40,height=40,
                             border_thickness=0, border_radius=5)

while True:
    visualizer.background_color("white")

    #===========
    # GRID
    #===========
    # columns
    for i in range(0, visualizer.wwidth, 150):
        visualizer.draw_line(start=(i,0),end=(i,visualizer.wheight),color=(179,204,204),width=1)

    # rows
    for j in range(0, visualizer.wheight, 150):
        visualizer.draw_line(start=(0,j),end=(visualizer.wwidth,j),color=(179,204,204),width=1)

    # loading the robot
    robot.load()

    # setting fps
    visualizer.set_fps(60)

    # reload
    visualizer.refresh_window()