import pygame
import json
import os

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ANIMATION_SPEED = 8

# Load the TMJ map
with open(r'rpg_game/testmap.tmj') as f:
    tmx_data = json.load(f)



    # Load the tileset image
    tileset_image_path = os.path.join(os.path.dirname(r"rpg_game/testmap.tmj"), tmx_data['tilesets'][0]['image'])
    tileset_image = pygame.image.load(tileset_image_path)

    # Check if the tileset is inline or external
    tileset = tmx_data['tilesets'][0]
    if 'image' in tileset:
        # Inline tileset
        tileset_image_path = os.path.join(os.path.dirname(r"rpg_game/testmap.tmj"), tmx_data['tilesets'][0]['image'])
        tileset_image = pygame.image.load(tileset_image_path)
    else:
        # External tileset
        tileset_path = os.path.join(os.path.dirname(r"rpg_game/testmap.tmj"), tileset['source'])
        with open(tileset_path) as f:
            tileset_data = json.load(f)
        tileset_image_path = os.path.join(os.path.dirname(tileset_path), tileset_data['image'])
        tileset_image = pygame.image.load(tileset_image_path)

    # Create screen object
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))



# Function to draw the map
def draw_map(surface, tmx_data, tileset_image):
    tile_width = tmx_data['tilewidth']
    tile_height = tmx_data['tileheight']
    tileset_columns = tileset_image.get_width() // tile_width

    for layer in tmx_data['layers']:
        if layer['type'] == 'tilelayer':
            width = tmx_data['width']
            for index, gid in enumerate(layer['data']):
                if gid > 0:  # gid 0 means no tile
                    x = index % width
                    y = index // width
                    tile_id = gid - tmx_data['tilesets'][0]['firstgid']
                    tile_x = (tile_id % tileset_columns) * tile_width
                    tile_y = (tile_id // tileset_columns) * tile_height
                    tile_rect = pygame.Rect(tile_x, tile_y, tile_width, tile_height)
                    surface.blit(tileset_image, (x * tile_width, y * tile_height), tile_rect)

# Draw the map
draw_map(screen, tmx_data, tileset_image)


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

# Load all animations
animations = {
    'down': {
        'idle': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_down idle.png', 5, 'idle'),
        'walk': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_down walk.png', 6, 'walk'),
        'attack': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_down attack.png', 4, 'attack'),
        'pickup': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_pick up.png', 5, 'pickup') 
    },
    'up': {
        'idle': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_up idle.png', 5, 'idle'),
        'walk': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_up walk.png', 6, 'walk'),
        'attack': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_up attack.png', 4, 'attack'),
        'pickup': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_pick up.png', 5, 'pickup') 
    },
    'left': {
        'idle': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_side idle.png', 5, 'idle'),
        'walk': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_side walk.png', 6, 'walk'),
        'attack': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_side attack.png', 3, 'attack'),
        'pickup': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_pick up.png', 5, 'pickup')
    },
    'right': {
        'idle': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_side idle.png', 5, 'idle', direction='right'),
        'walk': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_side walk.png', 6, 'walk', direction='right'),
        'attack': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_side attack.png', 3, 'attack', direction='right'),
        'pickup': load_sprite_sheet('C:/Users/speng/OneDrive/Desktop/Kyle_Capstone_Project/rpg_game/assets/character/_pick up.png', 5, 'pickup')
    }
}



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.direction = 'down'
        self.state = 'idle'
        self.image = animations[self.direction][self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_count = 0
        self.speed = 1
        self.facing_right = True  # Initially facing right
        self.attacking = False
        self.picking_up = False

    def move(self, dx, dy):
        if not self.attacking and not self.picking_up:  # Prevent movement during attack or pick-up
            if dx != 0 or dy != 0:
                self.state = 'walk'
                if dx != 0:
                    self.direction = 'right' if dx > 0 else 'left'
                    self.facing_right = dx > 0  # Update facing direction
                else:
                    self.direction = 'down' if dy > 0 else 'up'
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
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
        if self.state == 'attack':
            speed = ANIMATION_SPEED  
        frame_index = (self.animation_count // speed) % frames
        self.image = animations[self.direction][self.state][frame_index]
    
        if self.animation_count >= frames * speed:
            self.animation_count = 0
            if self.state == 'attack':
                self.attacking = False
                self.state = 'idle'
            elif self.state == 'picking_up':
                self.picking_up = False
                self.state = 'idle'




# Create your character
character = Player(100, 100)  # Starting position

# Keeps main loop running
running = True
# Setup the clock for a decent framerate
clock = pygame.time.Clock()
# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did user hit a key
        if event.type == KEYDOWN:
            # Was it the escape key?
            if event.key ==K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False

    # Handle input
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]:
        dx = -1
    if keys[pygame.K_RIGHT]:
        dx = 1
    if keys[pygame.K_UP]:
        dy = -1
    if keys[pygame.K_DOWN]:
        dy = 1

    character.move(dx, dy)
    character.update()

    # Drawing
    
    screen.fill((0, 0, 0))  # Clear screen
    screen.blit(character.image, character.rect) # Draw player
    
    clock.tick(100)
    pygame.display.flip() # updates display

    
pygame.quit()

