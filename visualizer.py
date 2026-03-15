from sajilopygame import *
from sajilocv import *

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
    data_from_serial = odometry_data.receive_serial_data()
    if data_from_serial is not None:
        print(data_from_serial)
        try:
            data = data_from_serial.decode('utf-8').strip()
            if data.startswith("L:") and " R:" in data:
                    parts = data.split(" R:")
                    left_enc = int(parts[0].replace("L:", ""))
                    right_enc = int(parts[1])
                    # print the values to the console
                    print(f"Left Encoder: {left_enc}, Right Encoder: {right_enc}")
        except:
            pass

    #============
    # KEY STROKES
    #============
    robot_speed = 5
    if visualizer.left_pressed:
        robot.update_position(xpos=robot.xpos-robot_speed,ypos=robot.ypos)
    if visualizer.right_pressed:
        robot.update_position(xpos=robot.xpos+robot_speed,ypos=robot.ypos)
    if visualizer.up_pressed:
        robot.update_position(xpos=robot.xpos,ypos=robot.ypos-robot_speed)
    if visualizer.down_pressed:
        robot.update_position(xpos=robot.xpos,ypos=robot.ypos+robot_speed)

    # title text
    visualizer.draw_text(text="Punte Robot Visualizer",font_size=20,color=(40,40,80),xpos=10,ypos=10)

    # setting fps
    visualizer.set_fps(60)

    # reload
    visualizer.refresh_window()