import pygame

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