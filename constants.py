import pathlib

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "Kyle_Capstone_Project-1" / "assets"

# How much force to put on the bullet
BULLET_MOVE_FORCE = 4500

# Make bullet less affected by gravity
BULLET_GRAVITY = 300

# Mass of the bullet
BULLET_MASS = 0.1

# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

# Friction between objects
DYNAMIC_ITEM_FRICTION = 0.6

# Gravity
GRAVITY = 1500

# Mass (defaults to 1)
PLAYER_MASS = 2.0

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

# Strength of a jump
PLAYER_JUMP_IMPULSE = 1000

# Friction between objects
PLAYER_FRICTION = 1.0

# Damping - Amount of speed lost per second
PLAYER_DAMPING = 0.4

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# Force applied when climbing
PLAYER_CLIMB_FORCE = 5000

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_TILES = 0.5

# How big are our image tiles?
SPRITE_IMAGE_SIZE = 128

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of grid to show on screen, in number of tiles
SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

# Size of screen to show, in pixels
SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# Screen title
SCREEN_TITLE = "RoboWars"

# Friction between objects
WALL_FRICTION = 0.7

# Enemy move speed
ENEMY_MOVE_SPEED = 2

# Distance to change enemy texture
ENEMY_TEXTURE_CHANGE_DISTANCE = 20

