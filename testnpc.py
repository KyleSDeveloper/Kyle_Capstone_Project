import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Welcome to Arcade"
CHARACTER_SCALING = 1.0
SPRITE_SHEET = "characters.png"
SPRITE_WIDTH = 32
SPRITE_HEIGHT = 32
SPRITE_MARGIN = 0
SPRITE_COUNT_X = 23  # Number of frames per row (except the last row)
SPRITE_COUNT_Y = 4   # Number of rows
LAST_ROW_FRAME_COUNT = 4  # Number of frames in the last row

# Classes
class Welcome(arcade.Window):
    """Main welcome window
    """
    def __init__(self):
        """Initialize the window
        """

        # Call the parent class constructor
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the background window
        arcade.set_background_color(arcade.color.AMAZON)

        # Load the sprite sheet
        self.character_textures = arcade.load_spritesheet(
            SPRITE_SHEET,
            SPRITE_WIDTH,
            SPRITE_HEIGHT,
            SPRITE_COUNT_X,
            SPRITE_COUNT_Y
        )

        # Create the character sprite
        self.character_sprite = arcade.Sprite()
        self.character_sprite.scale = CHARACTER_SCALING
        self.character_sprite.center_x = SCREEN_WIDTH // 2
        self.character_sprite.center_y = SCREEN_HEIGHT // 2

        # Set the initial texture
        self.set_animation_row(0)  # Set to the first row of animations

        # Animation variables
        self.current_texture_index = 0
        self.animation_speed = 0.1  # Adjust the speed of the animation
        self.time_since_last_frame = 0

    def set_animation_row(self, row):
        """Set the animation row
        """
        if row < 0 or row >= SPRITE_COUNT_Y:
            print(f"Error: Row {row} is out of range. Valid rows are 0 to {SPRITE_COUNT_Y - 1}.")
            return

        start_index = row * SPRITE_COUNT_X
        if row == SPRITE_COUNT_Y - 1:  # Last row
            end_index = start_index + LAST_ROW_FRAME_COUNT
        else:
            end_index = start_index + SPRITE_COUNT_X

        if end_index > len(self.character_textures):
            print(f"Error: Calculated end index {end_index} is out of range.")
            return

        self.character_sprite.textures = self.character_textures[start_index:end_index]
        self.character_sprite.set_texture(0)

    def on_draw(self):
        """Called whenever you need to draw your window
        """

        # Clear the screen and start drawing
        arcade.start_render()

        # Draw the character sprite
        self.character_sprite.draw()

    def on_update(self, delta_time):
        """Update the game state
        """
        # Update the animation
        self.time_since_last_frame += delta_time
        if self.time_since_last_frame > self.animation_speed:
            self.time_since_last_frame = 0
            self.current_texture_index += 1
            if self.current_texture_index >= len(self.character_sprite.textures):
                self.current_texture_index = 0
            self.character_sprite.set_texture(self.current_texture_index)

# Main code entry point
if __name__ == "__main__":
    window = Welcome()
    arcade.run()