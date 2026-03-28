from sajilopygame import *
from sajilocv import *
import threading
import queue
import os
import time

# instantiating the class
visualizer = sajilopygame(wwidth=1350, wheight=750)
serialData = sajilocv()
odometry_data = serialData.ucontroller(serialData,port='COM8',baudrate=115200,timeout=1)

# title of the window
visualizer.window_title("Odometry Visualizer")

# robot character
# actual width of the robot{l: 0.125m, b: 0.11m}
# since 1m = 150px, in visualizer l = 0.125 * 150 = 18.75px ; b = 0.11 * 150 = 16.5px
robot_world_width = 18.75
robot_world_height = 16.5
robot = visualizer.character(parent=visualizer,type="shape",character_shape="rectangle",
                             color=(232,28,79),org=(0,visualizer.wheight),width=robot_world_width,height=robot_world_height,
                             border_thickness=0, border_radius=5)

#===========
# ARROWS SETUP
#===========
# folder path for arrow images
arrow_folder = "assets/arrows"

# dictionary to hold arrow characters
arrows = {}

# resizing the arrows
target_width = 16
target_height = 16

for direction in ["up", "down", "left", "right"]:
    path = os.path.join(arrow_folder, f"{direction}.png")
    if os.path.exists(path):
        original = pygame.image.load(path).convert_alpha()

        # resizing
        resized = pygame.transform.smoothscale(original, (target_width, target_height))

        arrows[direction] = resized
    else:
        print(f"Warning: missing {direction}.png")

#===========
# ODOMETRY SETUP
#===========
# world coordinates
world_x = 0.0   # meters (right = positive)
world_y = 0.0   # meters (forward = positive)
heading = 90.0  # degrees (90 = facing up)

# NOTE:
# Calibrated: TICKS_PER_METER = 13000, scale = 156.5
# Achieved good quadrant alignment after physical motor centering + dual casters

# wheel constants
TICKS_PER_METER = 13000       # 9191.25
WHEEL_BASE = 0.127  # meters (distance between left and right wheels)

# previous encoder values
prev_left = 0
prev_right = 0

#===========
# MAP SETTINGS
#===========
obstacle_points = []  # list of (world_x, world_y) in meters

# TOF SENSOR OFFSET (tune these values)
sensor_offset_forward = 0.055   # meters: how far TOF is in front of robot center

#=========== TOF FILTER =================
tof_filtered = 0.0  # smoothed value
FILTER_ALPHA = 0.1 # 0.1 = very smooth, 0.4 = faster response


#===========
# GYROZ SETTINGS
#===========
gyro_heading = 90.0
last_gyro_time = 0.0
FUSION_ALPHA = 0.95          # trust gyro when moving

# New threshold to detect "movement"
MOVEMENT_THRESHOLD = 5       # minimum encoder ticks change to consider "moving"


# Caster wheel misalignment compensation
TURN_CORRECTION_FACTOR = 0.9     # Start with 1.0, tune this value

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
    visualizer.draw_rect(color=(74,243,255),org=(1150,10),width=150,height=75,border_thickness=0,border_radius=10)

    data_from_serial = odometry_data.receive_serial_data()

    if data_from_serial is not None:
        try:
            line = data_from_serial.strip()  # remove \n and extra spaces

            if line.startswith("L:") and ", R:" in line and ", TOF:" in line and ", GYROZ:" in line:
                # Split step by step on the known separators
                l_part = line.split(", R:")[0].strip()                # "L:1"
                r_part = line.split(", R:")[1].split(", TOF:")[0].strip()  # "426"
                tof_part = line.split(", TOF:")[1].split(", GYROZ:")[0].strip()  # "221"
                gyroz_part = line.split(", GYROZ:")[1].strip()        # "1.16"

                # Parse each value safely
                left_enc   = int(l_part.replace("L:", ""))
                right_enc  = int(r_part.replace("R:", ""))
                tof_raw    = int(tof_part)
                gyro_rate  = float(gyroz_part.replace("GYROZ:", ""))

                # Convert TOF safely
                try:
                    tof_distance = int(tof_raw)
                except ValueError:
                    tof_distance = -999   # error/invalid flag

                # Optional: debug print to console
                #print(f"L:{left_enc}  R:{right_enc}  TOF:{tof_raw}  GYROZ:{gyro_rate}")

        except Exception:
            # silently ignore bad packets during runtime
            # (uncomment next line only when debugging)
            # print("Bad packet:", data_from_serial)
            pass

    #========= TOF FILTERING ========
    # using Exponential Moving Average
    if tof_distance > 0:
        tof_filtered = (FILTER_ALPHA * tof_distance) + ((1 - FILTER_ALPHA) * tof_filtered)
    else:
        tof_filtered = 0    # invlaid reading  
    
    visualizer.draw_text(text="Encoder Data",font_size=16,color=(0,0,0),xpos=1155,ypos=15)
    visualizer.draw_text(text=f"Left: {left_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=35)
    visualizer.draw_text(text=f"Right: {right_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=55)

    #===========
    # TOF DATA
    #===========
    visualizer.draw_rect(color=(255, 179, 179),org=(1150,100),width=150,height=50,border_thickness=0,border_radius=10)
    visualizer.draw_text(text="TOF Data",font_size=16,color=(0,0,0),xpos=1155,ypos=105)
    visualizer.draw_text(text=f"Distance: {int(tof_filtered)}",font_size=16,color=(84,84,84),xpos=1155,ypos=125)

    #===========
    # ODOMETRY CALCULATIONS
    #===========
    # wheel diameter = 34 milimeters = 0.034 meters
    # wheel circumference = pi * diameter = 0.034 * 3.14159 = 0.1068 meters
    # wheel to wheel distance = 119 milimeters = 0.119 meters # new distance = 0.127m
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
    heading += delta_theta * (180.0 / math.pi)

    # Keep in 0–360°
    heading = heading % 360     # keeping the heading between 0 and 360 degrees
    
    visualizer.draw_rect(color=(179, 179, 179),org=(1150,170),width=150,height=50,border_thickness=0,border_radius=10)
    visualizer.draw_text(text="Gyro",font_size=16,color=(0,0,0),xpos=1155,ypos=175)
    visualizer.draw_text(text=f"Heading: {int(heading)}°",font_size=16,color=(84, 84, 84),xpos=1155,ypos=195)

    # update world position
    world_x += distance * math.cos(math.radians(heading))
    world_y += distance * math.sin(math.radians(heading))

    # save current encoder values for next loop
    prev_left = left_enc
    prev_right = right_enc

    # ==================== DRAW ROBOT AT CALCULATED POSITION ====================
    # Convert world coordinates to screen pixels
    scale = 156.5                     # 150 pixels = 1 meter (same as your grid)
    screen_x = 675 + int(world_x * scale)
    screen_y = 375 - int(world_y * scale)   # Y flipped because screen Y grows down

    # Update robot character position
    robot.update_position(xpos=screen_x - (robot_world_width//2), ypos=screen_y - (robot_world_height//2))

    robot.load()

    # draw heading arrow
    #visualizer.draw_text(text=f"Heading: {int(heading)}",font_size=16,color=(84,84,84),xpos=1155,ypos=165)
    if 45 <= heading < 135:
        direction = "up"
    elif 135 <= heading < 225:
        direction = "left"
    elif 225 <= heading < 315:
        direction = "down"
    else:
        direction = "right"   # includes 315–360 and 0–45

    # Draw the arrow centered on the robot
    if direction in arrows:
        img = arrows[direction]
        rect = img.get_rect(center=(screen_x, screen_y))
        visualizer.screen.blit(img, rect)


    #============
    # MAPPING
    #============
    # Draw all obstacle points on the screen from world coordinates
    for wx, wy in obstacle_points:
        screen_obx = 675 + int(wx * scale)
        screen_oby = 375 - int(wy * scale)  # Y flipped

        visualizer.draw_rect(color=(255,0,0),org=(screen_obx-5,screen_oby-5),width=2,height=2,border_thickness=0,border_radius=0)    

    if 50 < tof_filtered < 350:  # ignoring very close noise and far readings
        d_m = tof_filtered / 1000.0

        # calculating the actual position of the TOF sensor in world space
        sensor_x = world_x + sensor_offset_forward * math.cos(math.radians(heading))
        sensor_y = world_y + sensor_offset_forward * math.sin(math.radians(heading))

        # calculate obstacle position in pixels
        obs_world_x = sensor_x + d_m * math.cos(math.radians(heading))
        obs_world_y = sensor_y + d_m * math.sin(math.radians(heading))

        # storing in world coordinates
        # checking for unique points to store them in the varibale
        # minimum distance (in meters) to consider a point "unique"
        MIN_DIST_M = 0.003 # 0.3cm
        is_unique = True

        if obstacle_points:
            for px, py in obstacle_points:
                if math.hypot(obs_world_x - px, obs_world_y - py) < MIN_DIST_M:
                    is_unique = False
                    break

        if is_unique:
            obstacle_points.append((obs_world_x, obs_world_y))

        # prevent memory explosion
        if len(obstacle_points) > 2000:
            obstacle_points.pop(0)

    # drawing the newest obstacle point
    if obstacle_points:
        last_wx, last_wy = obstacle_points[-1]
        last_screen_x = 675 + int(last_wx * scale)
        last_screen_y = 375 - int(last_wy * scale)
        visualizer.draw_rect(color=(255,255,0), org=(last_screen_x-6, last_screen_y-6), width=12, height=12, border_radius=6)

    #============
    # KEY STROKES
    #============
    current_command = "STOP"    # sending data to punte for movement

    #robot_speed = 5
    if visualizer.left_pressed:
        current_command = "LEFT:90,90"
        #robot.update_position(xpos=robot.xpos-robot_speed,ypos=robot.ypos)
    if visualizer.right_pressed:
        current_command = "RIGHT:90,90"
        #robot.update_position(xpos=robot.xpos+robot_speed,ypos=robot.ypos)
    if visualizer.up_pressed:
        current_command = "FORWARD:122,110"
        #robot.update_position(xpos=robot.xpos,ypos=robot.ypos-robot_speed)
    if visualizer.down_pressed:
        current_command = "BACKWARD:128,115"
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