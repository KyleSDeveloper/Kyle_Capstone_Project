import pygame
from pytmx.util_pygame import load_pygame
import pytmx

pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ANIMATION_SPEED = 30
PLAYER_SPEED = 4

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D RPG")

# Load the map
tmxdata = load_pygame('rpg_game/assets/maps/untitled.tmx')

# Load sprite sheet
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
            if direction == 'right':
                frame = pygame.transform.flip(frame, True, False)
            animations.append(frame)
        else:
            print(f"Warning: Frame {i} for {state} at ({x}, {y}) is out of bounds. Skipping.")
    
    return animations

# Load all animations
animations = {
    'down': {'idle': load_sprite_sheet('rpg_game/assets/character/_down idle.png', 5, 'idle'),
             'walk': load_sprite_sheet('rpg_game/assets/character/_down walk.png', 6, 'walk'),
             'attack': load_sprite_sheet('rpg_game/assets/character/_down attack.png', 4, 'attack'),
             'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 5, 'pickup') },
    'up': {'idle': load_sprite_sheet('rpg_game/assets/character/_up idle.png', 5, 'idle'),
           'walk': load_sprite_sheet('rpg_game/assets/character/_up walk.png', 6, 'walk'),
           'attack': load_sprite_sheet('rpg_game/assets/character/_up attack.png', 4, 'attack'),
           'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 5, 'pickup') },
    'left': {'idle': load_sprite_sheet('rpg_game/assets/character/_side idle.png', 5, 'idle'),
             'walk': load_sprite_sheet('rpg_game/assets/character/_side walk.png', 6, 'walk'),
             'attack': load_sprite_sheet('rpg_game/assets/character/_side attack.png', 3, 'attack'),
             'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 5, 'pickup') },
    'right': {'idle': load_sprite_sheet('rpg_game/assets/character/_side idle.png', 5, 'idle', direction='right'),
              'walk': load_sprite_sheet('rpg_game/assets/character/_side walk.png', 6, 'walk', direction='right'),
              'attack': load_sprite_sheet('rpg_game/assets/character/_side attack.png', 3, 'attack', direction='right'),
              'pickup': load_sprite_sheet('rpg_game/assets/character/_pick up.png', 5, 'pickup') }
}

# Player setup
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animation_index = 0
        self.animation_speed = 0.15
        self.direction = 'down'
        self.action = 'idle'
        self.animation_frames = animations[self.direction][self.action]
        self.image = self.animation_frames[int(self.animation_index)]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        # Handle player movement based on key presses
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            self.direction = 'left'
            dx = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.direction = 'right'
            dx = PLAYER_SPEED
        elif keys[pygame.K_UP]:
            self.direction = 'up'
            dy = -PLAYER_SPEED
        elif keys[pygame.K_DOWN]:
            self.direction = 'down'
            dy = PLAYER_SPEED

        if dx != 0 or dy != 0:
            self.action = 'walk'
        else:
            self.action = 'idle'

         # Check for collisions before moving
        new_rect = self.rect.move(dx, dy)
        if self.check_collision(new_rect):
            # If collision detected, do not move
            dx, dy = 0, 0


        self.rect.x += dx
        self.rect.y += dy

         

        # Update animation
        self.animation_frames = animations[self.direction][self.action]
        self.animation_index += self.animation_speed
        if self.animation_index >= len(self.animation_frames):
            self.animation_index = 0

        self.image = self.animation_frames[int(self.animation_index)]

    def check_collision(self, new_rect):
        # This method checks if the new position collides with any obstacle on the collision layer
        for layer in tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == 'collision':
                for x, y, _ in layer.tiles():
                    tile_rect = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, 
                                            tmxdata.tilewidth, tmxdata.tileheight)
                    if new_rect.colliderect(tile_rect):
                        return True
        return False

# Initialize player
player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
all_sprites = pygame.sprite.Group(player)

# Camera setup
camera = pygame.math.Vector2(0, 0)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # Camera movement with boundary checks
    camera.x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, tmxdata.width * tmxdata.tilewidth - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.centery - SCREEN_HEIGHT // 2, tmxdata.height * tmxdata.tileheight - SCREEN_HEIGHT))

    # Draw the map
    for layer in tmxdata.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, image in layer.tiles():
                screen.blit(image, (x * tmxdata.tilewidth - camera.x, y * tmxdata.tileheight - camera.y))

    # Draw player
    screen.blit(player.image, (player.rect.x - camera.x, player.rect.y - camera.y))

    # Update display
    pygame.display.flip()
    
    # fps
    clock.tick(ANIMATION_SPEED) 

pygame.quit()