import pygame
from pytmx.util_pygame import load_pygame
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE,
)

# Initialize pygame
pygame.init()

# Window dimensions
WIDTH = 800
HEIGHT = 600
ANIMATION_SPEED = 8

# Create window object
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Load the map
tmxdata = load_pygame('rpg_game/assets/maps/testmap.tmx')

def load_sprite_sheet(path, frames, state, frame_width=64, frame_height=64, direction='left'):
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading sprite sheet: {e}")
        return []
    animations = []
    sheet_width, sheet_height = sheet.get_width(), sheet.get_height()
    
    for i in range(frames):
        x = (i * frame_width) % sheet_width
        y = (i * frame_width) // sheet_width * frame_height
        if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            animations.append(frame)
        else:
            print(f"Warning: Frame {i} for {state} at ({x}, {y}) is out of bounds. Skipping.")
    if direction == 'right':
        animations = [pygame.transform.flip(frame, True, False) for frame in animations]
    return animations

def blit_all_tiles(window, tmxdata, world_offset):
    for layer in tmxdata.visible_layers:
        for tile in layer.tiles():
            # tile[0] is the x grid location
            # tile[1] is the y grid location
            # tile[2] is the image data for blitting
            x_pixel = tile[0] * tmxdata.tilewidth + world_offset[0]
            y_pixel = tile[1] * tmxdata.tileheight + world_offset[1]
            window.blit(tile[2], (x_pixel, y_pixel))

# Health and mana bars
arial = pygame.font.SysFont("Arial", 18)
health = 100
mana = 100

# Load all animations
animations = {
    'down': {
        'idle': load_sprite_sheet('rpg_game/assets/character/_down idle.png', 5, 'idle'),
        'walk': load_sprite_sheet('rpg_game/assets/character/_down walk.png', 6, 'walk'),
        'attack': load_sprite_sheet('rpg_game/assets/character/_down attack.png', 1, 'attack'),
        'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 4, 'pickup')
    },
    'up': {
        'idle': load_sprite_sheet('rpg_game/assets/character/_up idle.png', 5, 'idle'),
        'walk': load_sprite_sheet('rpg_game/assets/character/_up walk.png', 6, 'walk'),
        'attack': load_sprite_sheet('rpg_game/assets/character/_up attack.png', 1, 'attack'),
        'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 4, 'pickup')
    },
    'left': {
        'idle': load_sprite_sheet('rpg_game/assets/character/_side idle.png', 5, 'idle'),
        'walk': load_sprite_sheet('rpg_game/assets/character/_side walk.png', 6, 'walk'),
        'attack': load_sprite_sheet('rpg_game/assets/character/_side attack.png', 1, 'attack'),
        'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 4, 'pickup')
    },
    'right': {
        'idle': load_sprite_sheet('rpg_game/assets/character/_side idle.png', 5, 'idle', direction='right'),
        'walk': load_sprite_sheet('rpg_game/assets/character/_side walk.png', 6, 'walk', direction='right'),
        'attack': load_sprite_sheet('rpg_game/assets/character/_side attack.png', 1, 'attack', direction='right'),
        'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 4, 'pickup')
    }
}

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.direction = 'down'
        self.state = 'idle'
        self.image = animations[self.direction][self.state][0]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.animation_count = 0
        self.speed = 1
        self.facing_right = True  # Initially facing right
        self.attacking = False
        self.picking_up = False

        # Define the box within which the player can move
        self.box_width = 1
        self.box_height = 1
        self.box_left = (WIDTH - self.box_width) // 2
        self.box_top = (HEIGHT - self.box_height) // 2
        self.box_right = self.box_left + self.box_width
        self.box_bottom = self.box_top + self.box_height

    def move(self, dx, dy):
        if not self.attacking and not self.picking_up:  # Prevent movement during attack or pick-up
            if dx != 0 or dy != 0:
                self.state = 'walk'
                if dx != 0:
                    self.direction = 'right' if dx > 0 else 'left'
                    self.facing_right = dx > 0  # Update facing direction
                else:
                    self.direction = 'down' if dy > 0 else 'up'

                # Calculate new position
                new_x = self.rect.x + dx * self.speed
                new_y = self.rect.y + dy * self.speed

                # Keep within the defined box limits
                if self.box_left <= new_x <= self.box_right - self.rect.width:
                    self.rect.x = new_x
                else:
                    world_offset[0] -= dx * self.speed

                if self.box_top <= new_y <= self.box_bottom - self.rect.height:
                    self.rect.y = new_y
                else:
                    world_offset[1] -= dy * self.speed
            else:
                self.state = 'idle'
    
    def attack(self):
        self.state = 'attack'
        self.attacking = True
        self.animation_count = 0

    def pick_up(self):
        self.state = 'pickup'
        self.picking_up = True
        self.animation_count = 0
    
    def update(self):
        self.animation_count += 1
        frames = len(animations[self.direction][self.state])
        speed = ANIMATION_SPEED
        frame_index = (self.animation_count // speed) % frames
        self.image = animations[self.direction][self.state][frame_index]
        if self.animation_count >= frames * speed:
            self.animation_count = 0
            if self.state == 'attack':
                self.attacking = False
                self.state = 'idle'
            elif self.state == 'pickup':
                self.picking_up = False
                self.state = 'idle'

# Create your character
character = Player()  

# Keeps main loop running
running = True

# Setup the clock for a decent framerate
clock = pygame.time.Clock()
world_offset = [0, 0]

# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did user hit a key
        if event.type == KEYDOWN:
            # Was it the escape key?
            if event.key == K_ESCAPE:
                running = False
            # Was it the space key? If so, attack.
            if event.key == K_SPACE:
                character.attack()
            # Was it 'e', if so, pickup.
            if event.key == pygame.K_e:
                character.pick_up()
        elif event.type == QUIT:
            running = False

    # Handle input
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_a]:
        dx = -1
    if keys[pygame.K_d]:
        dx = 1
    if keys[pygame.K_w]:
        dy = -1
    if keys[pygame.K_s]:
        dy = 1

    character.move(dx, dy)
    character.update()

    # Drawing
    window.fill((0, 0, 0))  # Clear screen

    # Blit all tiles
    blit_all_tiles(window, tmxdata, world_offset)

    # blit health and mana 
    health_image = arial.render("Health: "+str(health), 1, (255, 255, 255))
    mana_image = arial.render(f"Mana: {mana}", 1, (255, 255, 255))
    window.blit(health_image, (50, 10))
    window.blit(mana_image, (50, 30))
    
    # Draw player
    window.blit(character.image, character.rect)

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(75)
    pygame.display.flip()  # Updates display

pygame.quit()