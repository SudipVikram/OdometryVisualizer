import pygame
import math

pygame.init()

# Create the window
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Odometry Visualizer - Step 1")

# to control the loop speed
clock = pygame.time.Clock()

# colors
BG_COLOR = (245, 245, 240)  # warm gray
GRID_COLOR = (215, 220, 220)    # light gray
TEXT_COLOR = (60, 60, 80)
ROBOT_COLOR = (60, 130, 230)        # nice blue
ARROW_COLOR = (20, 20, 40)

running = True

while running:
    # Checking if the user clicked the close button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #----------------------
    # DRAWING
    #----------------------
    # Fill the screen with one color(black)
    screen.fill(BG_COLOR)

    # Draw a simple grid
    tile_size = 40     # each square is 40x40 pixels

    # vertical lines
    for x in range(0, WIDTH, tile_size):
        pygame.draw.line(screen, GRID_COLOR, (x,0),(x,HEIGHT),1)

    # Horizontal lines
    for y in range(0,HEIGHT,tile_size):
        pygame.draw.line(screen, GRID_COLOR, (0,y), (WIDTH,y),1)

    #--------------------
    # Robot
    #--------------------
    robot_center_x = WIDTH // 2
    robot_center_y = HEIGHT // 2

    # Robot body: rectangle 60px wide, 80px long
    robot_width = 60
    robot_length = 80

    # calculate the top-left corner of the rectangle(robot_center_x, robot_center_y)
    rect_x = robot_center_x - robot_width // 2
    rect_y = robot_center_y - robot_length // 2

    # draw the robot body
    pygame.draw.rect(
        screen,
        ROBOT_COLOR,
        (rect_x, rect_y, robot_width, robot_length),
        border_radius=8     # for rounded corners
    )

    # direction arrow
    arrow_length = 50
    # straight up from the center of the robot
    arrow_start = (robot_center_x, robot_center_y)
    arrow_end = (robot_center_x, robot_center_y - arrow_length)

    pygame.draw.line(screen, ARROW_COLOR, arrow_start, arrow_end, 5)
    pygame.draw.circle(screen, ARROW_COLOR, arrow_end, 8)   # arrowhead dot

    # Title
    font = pygame.font.SysFont("arial", 22)
    text = font.render("Punte Robot Visualizer",True,TEXT_COLOR)
    screen.blit(text,(10,10))

    # Showing what we drew
    pygame.display.flip()

    # Try to run @ ~60fps
    clock.tick(60)

# clean exit
pygame.quit()