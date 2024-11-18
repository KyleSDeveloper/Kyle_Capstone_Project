


class Platform(arcade.Sprite):
    """Platform class"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.color = arcade.color.BRICK_RED

    def draw(self):
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, self.color)



class ArcadeBasic(arcade.View):
    """Main game window"""

    def __init__(self, width: int, height: int, title: str):
    
        
        super().__init__()
        self.width = width
        self.height = height
        self.title = title

        # Create the camera
        self.camera = arcade.Camera(width, height)

        self.setup()

    def setup(self):
        """Set up the game and initialize the variables."""
       

        # Load the Tiled map
        self.tile_map = arcade.load_tilemap("platformerforest.tmx", scaling=TILE_SCALING)

        # Create the sprite lists
        self.player_list = arcade.SpriteList()

        # Ensure the layer name matches the one in your Tiled map
        try:
            self.platform_list = self.tile_map.sprite_lists["Platforms"]
        except KeyError:
            print("Error: 'Platforms' layer not found in the Tiled map.")
            self.platform_list = arcade.SpriteList()

        # Define frame width and height
        frame_width = 32
        frame_height = 32

        
        # Set the initial position of the player sprite
        self.player_sprite.center_x = SCREEN_WIDTH // 6
        self.player_sprite.center_y = SCREEN_HEIGHT // 6.3

        # Add the player sprite to the player list
        self.player_list.append(self.player_sprite)

        # Define the frames for the player animation
        self.frames = []
        self.reversed_frames = []
        self.running_frames = []
        self.reversed_running_frames = []

        for i in range(4):  # 4 frames in the first row
            frame = arcade.load_texture("characters.png", x=i*frame_width, y=0, width=frame_width, height=frame_height)
            keyframe = arcade.AnimationKeyframe(i, 125, frame)  # 125 ms per frame
            self.frames.append(keyframe)

            reversed_frame = arcade.load_texture("characters.png", x=i*frame_width, y=0, width=frame_width, height=frame_height, mirrored=True)
            reversed_keyframe = arcade.AnimationKeyframe(i, 125, reversed_frame)  # 125 ms per frame
            self.reversed_frames.append(reversed_keyframe)

        # Define the running frames (frames 15-18)
        for i in range(15, 19):
            frame = arcade.load_texture("characters.png", x=i*frame_width, y=0, width=frame_width, height=frame_height)
            keyframe = arcade.AnimationKeyframe(i, 125, frame)  # 125 ms per frame
            self.running_frames.append(keyframe)

            reversed_frame = arcade.load_texture("characters.png", x=i*frame_width, y=0, width=frame_width, height=frame_height, mirrored=True)
            reversed_keyframe = arcade.AnimationKeyframe(i, 125, reversed_frame)  # 125 ms per frame
            self.reversed_running_frames.append(reversed_keyframe)

        self.player_sprite.frames = self.frames

        # Set the initial texture and hit box for the player sprite
        self.player_sprite.texture = self.frames[0].texture
        self.player_sprite.set_hit_box(self.player_sprite.texture.hit_box_points)

        # Track the current state of keys
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Game over flag
        self.game_over = False

        # Load and play background music
        self.background_music = arcade.load_sound("forest.wav")
        arcade.play_sound(self.background_music, looping=True)

        # Load sound effects in the setup method
        self.jump_sound = arcade.load_sound("jump.wav")

        # Create enemy sprite list and add an enemy
        self.enemy_list = arcade.SpriteList()
        enemy = Enemy("sheet.png", 0.5)
        enemy.center_x = 600
        enemy.center_y = 300
        self.enemy_list.append(enemy)

        # Initialize score
        self.score = 0

    def on_update(self, delta_time: float):
        """Movement and game logic"""
        if self.game_over:
            return

        self.player_list.update_animation(delta_time)

        # Apply gravity
        self.player_sprite.change_y -= GRAVITY

        # Update player position based on key presses
        if self.left_pressed:
            self.player_sprite.center_x -= PLAYER_SPEED
            self.player_sprite.frames = self.reversed_running_frames
        elif self.right_pressed:
            self.player_sprite.center_x += PLAYER_SPEED
            self.player_sprite.frames = self.running_frames
        else:
            self.player_sprite.frames = self.frames

        # Update player position
        self.player_sprite.center_y += self.player_sprite.change_y

        # Check for collision with platforms
        collisions = arcade.check_for_collision_with_list(self.player_sprite, self.platform_list)
        if collisions:
            self.player_sprite.change_y = 0
            self.player_sprite.center_y = collisions[0].top + self.player_sprite.height / 2

        # Check if player has fallen off the screen
        if self.player_sprite.center_y < 0:
            self.game_over = True
            print("Game Over")

        # Update the camera to follow the player
        self.center_camera_to_player()

    def center_camera_to_player(self):
        """Centers the camera on the player"""
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let the camera go beyond the map boundaries
        screen_center_x = max(screen_center_x, 0)
        screen_center_y = max(screen_center_y, 0)

        self.camera.move_to((screen_center_x, screen_center_y))

    def on_draw(self):
        """Render the screen"""
        arcade.start_render()

        # Activate the camera
        self.camera.use()

        # Draw each layer of the tile map
        for layer in self.tile_map.sprite_lists.values():
            layer.draw()
        self.player_list.draw()
        self.enemy_list.draw()

        if self.game_over:
            arcade.draw_text("Game Over", self.camera.position[0] + SCREEN_WIDTH / 2, self.camera.position[1] + SCREEN_HEIGHT / 2,
                             arcade.color.WHITE, 54, anchor_x="center")
            arcade.draw_text("Press R to Restart", self.camera.position[0] + SCREEN_WIDTH / 2, self.camera.position[1] + SCREEN_HEIGHT / 2 - 60,
                             arcade.color.WHITE, 24, anchor_x="center")

        # In the on_draw method
        arcade.draw_text(f"Score: {self.score}", 10, 570, arcade.color.WHITE, 20)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed"""
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            # Only allow jumping if the player is on the ground
            if self.player_sprite.change_y == 0:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.ESCAPE:
            pause_menu = PauseMenu()
            pause_menu.window = self.window
            pause_menu.window.game_view = self
            self.window.show_view(pause_menu)
        elif key == arcade.key.R and self.game_over:
            self.setup()  # Restart the game

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released"""
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

class MainMenu(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Platformer Game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.WHITE, 54, anchor_x="center")
        arcade.draw_text("Press ENTER to Start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                         arcade.color.WHITE, 24, anchor_x="center")
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = ArcadeBasic(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
            self.window.show_view(game_view)

class PauseMenu(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.WHITE, 54, anchor_x="center")
        arcade.draw_text("Press ESC to Resume", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                         arcade.color.WHITE, 24, anchor_x="center")
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.window.game_view)

# Main code entry point
if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_menu = MainMenu()
    window.show_view(main_menu)
    arcade.run()