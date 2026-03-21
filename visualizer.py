from sajilopygame import *
from sajilocv import *
import threading
import queue
import os

# instantiating the class
visualizer = sajilopygame(wwidth=1350, wheight=750)
serialData = sajilocv()
odometry_data = serialData.ucontroller(serialData,port='COM8',baudrate=115200,timeout=1)

# title of the window
visualizer.window_title("Odometry Visualizer")

# robot character
robot = visualizer.character(parent=visualizer,type="shape",character_shape="rectangle",
                             color=(232,28,79),org=(0,visualizer.wheight-40),width=40,height=40,
                             border_thickness=0, border_radius=5)

#===========
# ARROWS SETUP
#===========
# folder path for arrow images
arrow_folder = "assets/arrows"

# dictionary to hold arrow characters
arrows = {}

for direction in ["up", "down", "left", "right"]:
    path = os.path.join(arrow_folder, f"{direction}.png")
    if os.path.exists(path):
        arrows[direction] = pygame.image.load(path).convert_alpha()
    else:
        print(f"Warning: missing {direction}.png")

#===========
# ODOMETRY SETUP
#===========
# world coordinates
world_x = 0.0   # meters (right = positive)
world_y = 0.0   # meters (forward = positive)
heading = 90.0  # degrees (90 = facing up)

# wheel constants
TICKS_PER_METER = 9191.25
WHEEL_BASE = 0.119  # meters (distance between left and right wheels)

# previous encoder values
prev_left = 0
prev_right = 0

#===========
# MAP SETTINGS
#===========
obstacle_points = []  # list to store detected obstacle positions

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

    #===========
    # ODOMETRY DATA
    #===========
    # placeholder for odometry data
    visualizer.draw_rect(color=(74,243,255),org=(1150,10),width=150,height=100,border_thickness=0,border_radius=10)

    data_from_serial = odometry_data.receive_serial_data()

    if data_from_serial is not None:
        try:
            line = data_from_serial.strip()  # remove \n and extra spaces

            if line.startswith("L:") and ", R:" in line and ", TOF:" in line:
                # Split on the two known separators
                parts = line.split(", R:")
                if len(parts) != 2:
                    raise ValueError("Missing R: part")

                left_part = parts[0].strip()                    # "L:1234"
                rest = parts[1].strip()                         # "5678, TOF:342"

                left_enc = int(left_part.replace("L:", ""))

                # Now split the rest on ", TOF:"
                right_tof = rest.split(", TOF:")
                if len(right_tof) != 2:
                    raise ValueError("Missing TOF part")

                right_enc = int(right_tof[0].strip())           # "5678"
                tof_str   = right_tof[1].strip()                # "342" or "-1"

                # Convert TOF safely
                try:
                    tof_distance = int(tof_str)
                except ValueError:
                    tof_distance = -999   # error/invalid flag

                # Now you have:
                # left_enc, right_enc, tof_distance

                # Optional: debug print
                # print(f"L:{left_enc}  R:{right_enc}  TOF:{tof_distance}")

        except Exception:
            # silently ignore bad packets during runtime
            # (uncomment next line only when debugging)
            # print("Bad packet:", data_from_serial)
            pass

    
    visualizer.draw_text(text="Encoder Data",font_size=16,color=(0,0,0),xpos=1155,ypos=15)
    visualizer.draw_text(text=f"Left: {left_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=35)
    visualizer.draw_text(text=f"Right: {right_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=55)

    #===========
    # TOF DATA
    #===========
    visualizer.draw_rect(color=(255, 179, 179),org=(1150,120),width=150,height=50,border_thickness=0,border_radius=10)
    visualizer.draw_text(text="TOF Data",font_size=16,color=(0,0,0),xpos=1155,ypos=125)
    visualizer.draw_text(text=f"Distance: {tof_distance}",font_size=16,color=(84,84,84),xpos=1155,ypos=145)

    #===========
    # ODOMETRY CALCULATIONS
    #===========
    # wheel diameter = 34 milimeters = 0.034 meters
    # wheel circumference = pi * diameter = 0.034 * 3.14159 = 0.1068 meters
    # wheel to wheel distance = 119 milimeters = 0.119 meters
    # how many ticks since last update
    delta_left = left_enc - prev_left
    delta_right = right_enc - prev_right

    # convert ticks to distance
    dist_left = delta_left / TICKS_PER_METER
    dist_right = delta_right / TICKS_PER_METER

    # distance the robot center moved forward
    distance = (dist_left + dist_right) / 2.0

    # how much the robot turned (in radians)
    delta_theta = (dist_right - dist_left) / WHEEL_BASE

    # update heading (convert to degrees)
    heading += delta_theta * (180.0 / 3.14159)

    # update world position
    world_x += distance * math.cos(math.radians(heading))
    world_y += distance * math.sin(math.radians(heading))

    # save current encoder values for next loop
    prev_left = left_enc
    prev_right = right_enc

    # ==================== DRAW ROBOT AT CALCULATED POSITION ====================
    # Convert world coordinates to screen pixels
    scale = 150                     # 150 pixels = 1 meter (same as your grid)
    screen_x = 675 + int(world_x * scale)
    screen_y = 375 - int(world_y * scale)   # Y flipped because screen Y grows down

    # Update robot character position
    robot.update_position(xpos=screen_x - 20, ypos=screen_y - 30 + 85)

    robot.load()

    # draw heading arrow
    heading_norm = heading % 360
    if 45 <= heading_norm < 135:
        direction = "up"
    elif 135 <= heading_norm < 225:
        direction = "left"
    elif 225 <= heading_norm < 315:
        direction = "down"
    else:
        direction = "right"   # includes 315–360 and 0–45

    # Draw the arrow centered on the robot
    if direction in arrows:
        img = arrows[direction]
        rect = img.get_rect(center=(screen_x, screen_y + 75))
        visualizer.screen.blit(img, rect)


    #============
    # MAPPING
    #============
    if obstacle_points:
        # drawing the obstacle points
        for point_x, point_y in obstacle_points:
            visualizer.draw_rect(color=(255,0,0),org=(point_x-5,point_y-5),width=2,height=2,border_thickness=0,border_radius=0)

    if tof_distance > 0 and tof_distance < 200:
        # according to our calculations, the pixel to meter ratio is 150px per meter
        # tof_distance is in millimeters, so converting to meters we get
        tof_in_meters = tof_distance / 1000
        # distance the obstacle is from the robot in pixels
        obstacle_in_pixels = int(tof_in_meters * scale)
        # draw a point at the detected obstacle location
        # we have to consider the heading of the robot to draw the point in the correct direction
        obstacle_x = screen_x + int(obstacle_in_pixels * math.cos(math.radians(heading)))
        obstacle_y = screen_y - int(obstacle_in_pixels * math.sin(math.radians(heading)))

        obstacle_points.append((obstacle_x, obstacle_y))  # store for future use

        # drawing the newest obstacle point
        visualizer.draw_rect(color=(255,255,0),org=(obstacle_x-5,obstacle_y-5),width=10,height=10,border_thickness=0,border_radius=5)


    #============
    # KEY STROKES
    #============
    current_command = "STOP"    # sending data to punte for movement

    #robot_speed = 5
    if visualizer.left_pressed:
        current_command = "LEFT"
        #robot.update_position(xpos=robot.xpos-robot_speed,ypos=robot.ypos)
    if visualizer.right_pressed:
        current_command = "RIGHT"
        #robot.update_position(xpos=robot.xpos+robot_speed,ypos=robot.ypos)
    if visualizer.up_pressed:
        current_command = "FORWARD"
        #robot.update_position(xpos=robot.xpos,ypos=robot.ypos-robot_speed)
    if visualizer.down_pressed:
        current_command = "BACKWARD"
        #robot.update_position(xpos=robot.xpos,ypos=robot.ypos+robot_speed)

    #=============
    # sending command to punte
    #=============
    odometry_data.send_serial_data_unobstructed((current_command + "\n").encode("ascii"))

    # title text
    visualizer.draw_text(text="Punte Robot Visualizer",font_size=20,color=(40,40,80),xpos=10,ypos=10)
        
    # loading the robot
    #robot.load()

    # setting fps
    visualizer.set_fps(60)

    # reload
    visualizer.refresh_window()