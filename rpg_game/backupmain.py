import pygame
import sys
from pytmx.util_pygame import load_pygame
import pytmx

pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D RPG")

# Map loading
tmxdata = load_pygame('rpg_game/assets/maps/untitled.tmx')

# Helper function to render the map
def blit_all_tiles(window, tmxdata, world_offset):
    for layer in tmxdata:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmxdata.get_tile_image_by_gid(gid)
                if tile:
                    window.blit(tile, (x * tmxdata.tilewidth + world_offset[0], 
                                       y * tmxdata.tileheight + world_offset[1]))

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
    def __init__(self, solid_tiles):
        super().__init__()
        self.animations = animations
        self.image = self.animations['down']['idle'][0]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 2
        self.direction = "down"
        self.state = "idle"
        self.animation_index = 0
        self.animation_speed = 8  # adjust this to change animation speed
        self.last_update = pygame.time.get_ticks()
        self.attacking = False
        self.picking_up = False
        self.solid_tiles = solid_tiles
        self.world_offset = [0, 0]  # Added world offset for camera movement

    def move(self, dx, dy):
        # Adjust world offset
        self.world_offset[0] -= dx  # world moves opposite to player's local movement
        self.world_offset[1] -= dy
        
        # Create a rectangle for where the player will be after moving
        new_rect = self.rect.copy()
        new_rect.x += dx
        new_rect.y += dy

        # Check for collision with solid tiles using world offset
        for tile in self.solid_tiles:
            if new_rect.colliderect(tile.move(*self.world_offset)):
                # If there's a collision, we need to adjust the movement
                if dx > 0:  # Moving right
                    new_rect.right = tile.left - self.world_offset[0]
                elif dx < 0:  # Moving left
                    new_rect.left = tile.right - self.world_offset[0]
                if dy > 0:  # Moving down
                    new_rect.bottom = tile.top - self.world_offset[1]
                elif dy < 0:  # Moving up
                    new_rect.top = tile.bottom - self.world_offset[1]
        
        # Only update the player's position if there's no collision or if we've adjusted it
        self.rect = new_rect

    def update(self, keyspressed):
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 / self.animation_speed:
            self.last_update = now
            self.animation_index += 1
            if self.attacking or self.picking_up:
                if self.animation_index >= len(self.animations[self.direction][self.state]):
                    self.animation_index = 0
                    self.state = "idle"  # Return to idle after animation
                    self.attacking = False
                    self.picking_up = False
            else:
                self.animation_index %= len(self.animations[self.direction][self.state])
            self.image = self.animations[self.direction][self.state][self.animation_index]

        dx, dy = 0, 0
        if keyspressed[pygame.K_a]:  # Move left
            dx = -self.speed
            self.direction = "left"
            self.state = "walk"
        elif keyspressed[pygame.K_d]:  # Move right
            dx = self.speed
            self.direction = "right"
            self.state = "walk"
        elif keyspressed[pygame.K_w]:  # Move up
            dy = -self.speed
            self.direction = "up"
            self.state = "walk"
        elif keyspressed[pygame.K_s]:  # Move down
            dy = self.speed
            self.direction = "down"
            self.state = "walk"
        elif keyspressed[pygame.K_SPACE] and not self.attacking:  # Attack
            self.attacking = True
            self.state = "attack"
            self.animation_index = 0
        elif keyspressed[pygame.K_e] and not self.picking_up:  # Pick up
            self.picking_up = True
            self.state = "pickup"
            self.animation_index = 0
        else:
            if not self.attacking and not self.picking_up:
                self.state = "idle"

        # Check for collisions before moving
        self.move(dx, dy)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Main game loop
def game_loop():
    # Gather solid tiles
    solid_tiles = []
    for layer in tmxdata.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile_properties = tmxdata.get_tile_properties_by_gid(gid)
                if tile_properties and tile_properties.get('solid'):
                    solid_tiles.append(pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight))

    player = Player(solid_tiles)  # Pass solid_tiles to Player
    all_sprites = pygame.sprite.Group(player)
    clock = pygame.time.Clock()

    running = True
    world_offset = [0, 0]  # Camera offset

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Fill the screen with black
        # Render map
        blit_all_tiles(screen, tmxdata, player.world_offset)
        
        all_sprites.update(pygame.key.get_pressed())
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
