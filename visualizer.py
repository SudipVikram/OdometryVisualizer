from sajilopygame import *
from sajilocv import *
import threading
import queue

# instantiating the class
visualizer = sajilopygame(wwidth=1350, wheight=750)
serialData = sajilocv()
odometry_data = serialData.ucontroller(serialData,port='COM8',baudrate=115200,timeout=1)

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

    #===========
    # NUMBERING
    #===========
    f_size = 40
    counter = 1

    # outer loop controls vertical position (starting at y=645 and going up)
    for j in range(635, 0, -145):
        # inner loop controls horizontal position (150-pixel steps)
        for i in range(150, visualizer.wwidth + 150, 150):
            if counter <= 45:
                # draw the current number
                visualizer.draw_text(text=str(counter),font_size=f_size,color=(237, 237, 237),xpos=(i - 75 - (f_size // 2)),ypos=j)
                counter += 1
            else:
                break  # Stop once we reach 45

    
    # loading the robot
    robot.load()

    #===========
    # ODOMETRY DATA
    #===========
    # placeholder for odometry data
    visualizer.draw_rect(color=(74,243,255),org=(1150,10),width=150,height=100,border_thickness=0,border_radius=10)

    data_from_serial = odometry_data.receive_serial_data()
    if data_from_serial is not None:
        try:
            if data_from_serial.startswith("L:") and " R:" in data_from_serial:
                parts = data_from_serial.split(" R:")
                left_enc = int(parts[0].replace("L:", ""))
                right_enc = int(parts[1])
                # print the values to the console
                #print(f"Left Encoder: {left_enc}, Right Encoder: {right_enc}")
        except:
            pass

    
    visualizer.draw_text(text="Encoder Data",font_size=16,color=(0,0,0),xpos=1155,ypos=15)
    visualizer.draw_text(text=f"Left: {left_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=35)
    visualizer.draw_text(text=f"Right: {right_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=55)

    #============
    # KEY STROKES
    #============
    '''current_command = "STOP"    # sending data to punte for movement

    robot_speed = 5
    if visualizer.left_pressed:
        current_command = "LEFT"
        robot.update_position(xpos=robot.xpos-robot_speed,ypos=robot.ypos)
    if visualizer.right_pressed:
        current_command = "RIGHT"
        robot.update_position(xpos=robot.xpos+robot_speed,ypos=robot.ypos)
    if visualizer.up_pressed:
        current_command = "FORWARD"
        robot.update_position(xpos=robot.xpos,ypos=robot.ypos-robot_speed)
    if visualizer.down_pressed:
        current_command = "BACKWARD"
        robot.update_position(xpos=robot.xpos,ypos=robot.ypos+robot_speed)'''

    # title text
    visualizer.draw_text(text="Punte Robot Visualizer",font_size=20,color=(40,40,80),xpos=10,ypos=10)

    # setting fps
    visualizer.set_fps(60)

    # reload
    visualizer.refresh_window()