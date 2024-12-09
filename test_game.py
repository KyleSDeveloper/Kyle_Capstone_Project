import unittest
import arcade
from main import GameWindow, GameOverView  # Adjust the import based on your file structure

class TestGame(unittest.TestCase):
    def setUp(self):
        self.window = GameWindow(800, 600, "Test Game")
        self.window.setup()

    def test_game_window(self):
        self.assertIsInstance(self.window, arcade.Window)

    def test_game_over_view(self):
        self.assertIsInstance(GameOverView(), arcade.View)

    def test_player_die_switches_to_game_over_view(self):
        """Test if the game over screen displays when the player dies"""
        self.window.player_die()
        self.assertIsInstance(self.window.current_view, GameOverView)

if __name__ == '__main__':
    unittest.main()