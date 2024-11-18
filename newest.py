# Description: This is the newest version of the game. It will be the final version of the game.
# Imports
import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Welcome to Arcade"
CHARACTER_SCALING = 1

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

        # Load the character sprite
        self.character_sprite = arcade.Sprite("characters.png", CHARACTER_SCALING)
        self.character_sprite.center_x = SCREEN_WIDTH // 2

    def on_draw(self):
        """Called whenever you need to draw your window
        """

        # Clear the screen and start drawing
        arcade.start_render()

        # Draw the character sprite
        self.character_sprite.draw()

# Main code entry point
if __name__ == "__main__":
    app = Welcome()
    arcade.run()


