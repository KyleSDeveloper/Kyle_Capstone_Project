import logging
from typing import NoReturn
from views import TitleView
import arcade
import constants as game

def main() -> NoReturn:
    """Initialize and run the game window."""
    try:
        window = arcade.Window(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, game.SCREEN_TITLE)
        title_view = TitleView()
        window.show_view(title_view)
        arcade.run()
    except Exception as e:
        logging.error(f"An error occurred while initializing the game: {e}")

if __name__ == "__main__":
    main()
