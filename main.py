import arcade
import constants as game

def main():
    from views import TitleView
    """ Main function """
    window = arcade.Window(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, game.SCREEN_TITLE)
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()

if __name__ == "__main__":

    main()
