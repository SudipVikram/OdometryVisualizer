from sajilopygame import *
from sajilocv import *
import time
import math

# Initialize
visualizer = sajilopygame(wwidth=800, wheight=600)
visualizer.window_title("MPU6050 Gyro Test - Rotate the Robot")

serialData = sajilocv()
odometry_data = serialData.ucontroller(serialData, port='COM8', baudrate=115200, timeout=1)

arrow_size = 100   # size of the arrow

# Starting heading
heading = 90.0

while True:
    visualizer.background_color((30, 30, 40))

    # Receive data from ESP32
    data = odometry_data.receive_serial_data()
    
    gyro_rate = 0.0
    if data and "GYROZ:" in data:
        try:
            gyroz_part = data.split("GYROZ:")[-1].strip()
            gyro_rate = float(gyroz_part)
        except:
            pass

    # Integrate gyro rate
    dt = 0.05  # approximate time step
    heading += gyro_rate * dt
    heading = heading % 360

    # Center of screen
    cx, cy = 400, 300

    # Calculate tip of arrow
    rad = math.radians(heading)
    tip_x = cx + arrow_size * math.cos(rad)
    tip_y = cy + arrow_size * math.sin(rad)

    # Draw arrow shaft
    visualizer.draw_line((cx, cy), (tip_x, tip_y), color=(0, 255, 100), width=10)

    # Draw arrow head (triangle)
    head_size = 25
    head1_x = tip_x + head_size * math.cos(rad + 2.5)
    head1_y = tip_y + head_size * math.sin(rad + 2.5)
    head2_x = tip_x + head_size * math.cos(rad - 2.5)
    head2_y = tip_y + head_size * math.sin(rad - 2.5)

    visualizer.draw_polygon(color=(0, 255, 100), 
                            points=[(tip_x, tip_y), (head1_x, head1_y), (head2_x, head2_y)])

    # Info text
    visualizer.draw_text(text=f"Gyro Rate: {gyro_rate:.2f} °/s", 
                         font_size=20, color=(255,255,255), xpos=20, ypos=20)
    visualizer.draw_text(text=f"Heading: {heading:.1f}°", 
                         font_size=24, color=(255,255,255), xpos=20, ypos=50)
    visualizer.draw_text(text="Rotate the robot by hand", 
                         font_size=18, color=(200,200,200), xpos=20, ypos=550)

    # Show quadrant labels for reference
    visualizer.draw_text(text="90° ↑", font_size=18, color=(150,150,255), xpos=390, ypos=100)
    visualizer.draw_text(text="0° →", font_size=18, color=(150,150,255), xpos=680, ypos=290)
    visualizer.draw_text(text="270° ↓", font_size=18, color=(150,150,255), xpos=390, ypos=480)
    visualizer.draw_text(text="180° ←", font_size=18, color=(150,150,255), xpos=100, ypos=290)

    visualizer.refresh_window()