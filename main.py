import pygame
import math
from collections import deque

pygame.init()

# Create the window
WIDTH = 1400
HEIGHT = 700
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

# Robot in world coordinates (logical units)
robot_world_x = 0.0
robot_world_y = 0.0

# heading angle in degrees
heading_angle = 90.0          # 90° = up (in pygame angles: 0=right, 90=up, 180=left, 270=down)

# robot trail
trail = deque(maxlen=80)           # keep last 80 positions, then oldest disappears
trail_color = (80, 140, 220, 140)  # semi-transparent blue

# how many world units to move per frame when key is pressed
#move_speed = 0.08   # small steps for smooth movement
move_speed = 0.04     # slower / more precise

# show the coordinates of the robot
show_coords = True          # you can set to False later to hide

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
    tile_size = 140     # each square is 140x140 pixels

    max_x = (WIDTH  // tile_size) - 0.5     # center of last column
    max_y = (HEIGHT // tile_size) - 0.5     # center of top row

    # vertical lines
    for x in range(0, WIDTH, tile_size):
        pygame.draw.line(screen, GRID_COLOR, (x,0),(x,HEIGHT),1)

    # Horizontal lines
    for y in range(0,HEIGHT,tile_size):
        pygame.draw.line(screen, GRID_COLOR, (0,y), (WIDTH,y),1)

    # keeping the robot with the boundary
    robot_world_x = max(0.0, min(max_x, robot_world_x))
    robot_world_y = max(0.0, min(max_y, robot_world_y))

    for i, (wx, wy) in enumerate(trail):
        px = int(wx * tile_size + tile_size // 2)
        py = int(HEIGHT - (wy * tile_size + tile_size // 2))
        alpha = int(60 + 140 * (i / len(trail)))      # fade out older points
        color = (*trail_color[:3], alpha)
        pygame.draw.circle(screen, color, (px, py), 1)

    # ---------------------
    #   TILE NUMBERS
    # ---------------------

    # ── Simple tile numbering: 0, 1, 2, 3, … in center ────────────────
    font_tile = pygame.font.SysFont("consolas", 28, bold=False)   # big font

    # how many tiles fit
    cols = (WIDTH  + tile_size - 1) // tile_size
    rows = (HEIGHT + tile_size - 1) // tile_size

    tile_counter = 0

    for row in range(rows):
        for col in range(cols):
            # center of this tile
            cx = col * tile_size + tile_size // 2
            cy = row * tile_size + tile_size // 2

            # number as string
            number_str = str(tile_counter)

            text = font_tile.render(number_str, True, (221, 221, 238))  # medium gray
            text_rect = text.get_rect(center=(cx, cy))

            screen.blit(text, text_rect)

            tile_counter += 1

    # ── Axis labels (like a graph / plot) ───────────────────────────────

    # Font for axis numbers
    font_axis = pygame.font.SysFont("consolas", 14)

    # ── X labels (bottom edge) ────────────────────────────────
    max_col = (WIDTH  // tile_size)
    for col in range(1, max_col):
        x_pos = col * tile_size + tile_size // 2
        label = str(col * tile_size)          # actual pixel value or just tile index?
        # Option 1: show tile count (0,1,2,3...)
        label = str(col)
        # Option 2: show real pixel distance from left
        # label = str(col * tile_size)

        text = font_axis.render(label, True, (90, 90, 110))
        text_rect = text.get_rect(midtop=(x_pos, HEIGHT - 18))  # just above bottom edge
        screen.blit(text, text_rect)

    # ── Y labels (left edge) ──────────────────────────────────
    max_row = (HEIGHT // tile_size)
    for row in range(max_row):
        screen_x = 10                               # near left
        screen_y = HEIGHT - (row * tile_size + tile_size // 2)
        text = font_axis.render(str(row), True, (90,90,110))
        screen.blit(text, text.get_rect(midright=(screen_x, screen_y)))
        

    #--------------------
    # Robot
    #--------------------
        # ── Robot position in screen pixels (converted from world coordinates) ──
    robot_screen_x = int(robot_world_x * tile_size + tile_size // 2)
    robot_screen_y = int(HEIGHT - (robot_world_y * tile_size + tile_size // 2))

    # Robot body size (in pixels)
    robot_width_px  = 50
    robot_length_px = 50

    # Rectangle top-left corner
    rect_x = robot_screen_x - robot_width_px // 2
    rect_y = robot_screen_y - robot_length_px // 2

    pygame.draw.rect(
        screen,
        ROBOT_COLOR,
        (rect_x, rect_y, robot_width_px, robot_length_px),
        border_radius=8
    )

    # ── Direction arrow – rotated
    arrow_length_px = 50

    # Vector pointing in heading direction
    dx = math.cos(math.radians(heading_angle)) * arrow_length_px
    dy = -math.sin(math.radians(heading_angle)) * arrow_length_px   # negative because y grows up

    arrow_start = (robot_screen_x, robot_screen_y)
    arrow_end   = (robot_screen_x + dx, robot_screen_y + dy)

    pygame.draw.line(screen, ARROW_COLOR, arrow_start, arrow_end, 5)
    pygame.draw.circle(screen, ARROW_COLOR, (int(arrow_end[0]), int(arrow_end[1])), 8)

    if show_coords:
        font_coords = pygame.font.SysFont("consolas", 18)
        coord_text = f"x:{robot_world_x:5.1f}  y:{robot_world_y:5.1f}"
        text_surf = font_coords.render(coord_text, True, (40, 40, 80))
        text_rect = text_surf.get_rect(midbottom=(robot_screen_x, robot_screen_y - 65))
        # small background rectangle so text is readable on grid
        bg_rect = text_rect.inflate(12, 8)
        pygame.draw.rect(screen, (255,255,255,180), bg_rect, border_radius=4)
        screen.blit(text_surf, text_rect)                                                                               

    # Title
    font = pygame.font.SysFont("arial", 22)
    text = font.render("Punte Robot Visualizer",True,TEXT_COLOR)
    screen.blit(text,(10,10))

    # ── Keyboard input ───────────────────────────────────────────────
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        robot_world_x -= move_speed
        heading_angle = 180
    if keys[pygame.K_RIGHT]:
        robot_world_x += move_speed
        heading_angle = 0
    if keys[pygame.K_UP]:
        robot_world_y += move_speed
        heading_angle = 90
    if keys[pygame.K_DOWN]:
        robot_world_y -= move_speed
        heading_angle = 270

    trail.append((robot_world_x, robot_world_y))

    # Showing what we drew
    pygame.display.flip()

    # Try to run @ ~60fps
    clock.tick(60)

# clean exit
pygame.quit()