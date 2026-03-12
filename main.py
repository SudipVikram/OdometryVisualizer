import pygame
import math

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

    # vertical lines
    for x in range(0, WIDTH, tile_size):
        pygame.draw.line(screen, GRID_COLOR, (x,0),(x,HEIGHT),1)

    # Horizontal lines
    for y in range(0,HEIGHT,tile_size):
        pygame.draw.line(screen, GRID_COLOR, (0,y), (WIDTH,y),1)

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

            text = font_tile.render(number_str, True, (220, 220, 255))  # medium gray
            text_rect = text.get_rect(center=(cx, cy))

            screen.blit(text, text_rect)

            tile_counter += 1

    # ── Axis labels (like a graph / plot) ───────────────────────────────

    # Font for axis numbers
    font_axis = pygame.font.SysFont("consolas", 14)

    # ── X labels (bottom edge) ────────────────────────────────
    for col in range(0, cols + 1):  # +1 to include the last one
        x_pos = col * tile_size
        label = str(col * tile_size)          # actual pixel value or just tile index?
        # Option 1: show tile count (0,1,2,3...)
        # label = str(col)
        # Option 2: show real pixel distance from left
        # label = str(col * tile_size)

        text = font_axis.render(label, True, (90, 90, 110))
        text_rect = text.get_rect(midtop=(x_pos, HEIGHT - 18))  # just above bottom edge
        screen.blit(text, text_rect)

    # ── Y labels (left edge) ──────────────────────────────────
    for row in range(0, rows + 1):
        y_pos = row * tile_size
        label = str(row * tile_size)          # or str(row) for tile count

        text = font_axis.render(label, True, (90, 90, 110))
        text_rect = text.get_rect(midright=(18, y_pos))  # just right of left edge
        screen.blit(text, text_rect)

    # Optional: mark (0,0) more clearly
    pygame.draw.circle(screen, (220, 80, 80), (0, 0), 6)  # small red dot at top-left origin

    #--------------------
    # Robot
    #--------------------
    robot_center_x = WIDTH // 2
    robot_center_y = HEIGHT // 2

    # Robot body: rectangle 40px wide, 60px long
    robot_width = 40
    robot_length = 60

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