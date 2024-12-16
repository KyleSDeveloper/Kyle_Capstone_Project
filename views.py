import arcade
import math
import constants as game
from entities import Player
from typing import Optional

class TitleView(arcade.View):
    """Displays a title screen and prompts the user to begin the game.
    Provides a way to show instructions and start the game.
    """
    def __init__(self) -> None:
        super().__init__()

        # Find the title image in the images folder
        title_image_path = "assets/images/title_image.png"
        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)
        # Set our display timer
        self.display_timer = 3.0
        # Are we showing the instructions?
        self.show_instructions = False

    def on_draw(self) -> None:
    # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            center_x=game.SCREEN_WIDTH / 2,
            center_y=game.SCREEN_HEIGHT / 2,
            width=game.SCREEN_WIDTH,
            height=game.SCREEN_HEIGHT,
            texture=self.title_image,
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                "Enter to Start | I for Instructions",
                start_x=100,
                start_y=220,
                color=arcade.color.INDIGO,
                font_size=40,
            )
        
    def on_key_press(self, key: int, modifiers: int) -> None:
        """Resume the game when the user presses ESC again

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.I:
            instructions_view = InstructionsView()
            self.window.show_view(instructions_view)

class InstructionsView(arcade.View):
    """Show instructions to the player"""

    def __init__(self) -> None:
        """Create instructions screen"""
        super().__init__()

        instructions_image_path = "assets/images/instructions_image.png"

        # Load our title image
        self.instructions_image = arcade.load_texture(instructions_image_path)

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with the instructions image
        arcade.draw_texture_rectangle(
            center_x=game.SCREEN_WIDTH / 2,
            center_y=game.SCREEN_HEIGHT / 2,
            width=game.SCREEN_WIDTH,
            height=game.SCREEN_HEIGHT,
            texture=self.instructions_image,
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Start the game when the user presses Enter

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        elif key == arcade.key.ESCAPE:
            title_view = TitleView()
            self.window.show_view(title_view)

# Pause view, used when the player pauses the game
class PauseView(arcade.View):
    """Shown when the game is paused"""

    def __init__(self, game_view: arcade.View) -> None:
        """Create the pause screen"""
        # Initialize the parent
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Store a semi-transparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self) -> None:
        """Draw the underlying screen, blurred, then the Paused text"""

        self.game_view.on_draw()

        arcade.draw_lrtb_rectangle_filled(
            left=self.game_view.view_left,
            right=self.game_view.view_left + game.SCREEN_WIDTH,
            top=self.game_view.view_bottom + game.SCREEN_HEIGHT,
            bottom=self.game_view.view_bottom,
            color=self.fill_color,
        )

        # Now show the Pause text
        arcade.draw_text(
            "PAUSED - ESC TO CONTINUE",
            start_x=self.game_view.view_left + 180,
            start_y=self.game_view.view_bottom + 300,
            color=arcade.color.INDIGO,
            font_size=40,
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Resume the game when the user presses ESC again

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

class GameView(arcade.View):
    """ Main Window """
    def __init__(self):
        super().__init__()
        self.display_timer = 0
        self.view_left = 0
        self.view_bottom = 0
        self.level = 1
        
        
        
         # Player sprite
        self.player_sprite: Optional[Player] = None
        self.camera = None
        
        # Sprite lists
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.moving_sprites_list: Optional[arcade.SpriteList] = None
        self.ladder_list: Optional[arcade.SpriteList] = None
        self.enemy_list: Optional[arcade.SpriteList] = None
        self.goal_list: Optional[arcade.SpriteList] = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

        # Physics engine
        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None

        # Set background color
        arcade.set_background_color(arcade.color.SILVER_LAKE_BLUE)
        self.end_of_map = 0

        # Keep track of the score
        self.score = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        """ Set up everything with the game """
        # Set up the Camera
        self.camera = arcade.Camera(self.window.width, self.window.height)

        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Map name
        map_name = f"level_{self.level}.json"
        map_path = game.ASSETS_PATH / "maps" / map_name
        
        # Load in TileMap
        tile_map = arcade.load_tilemap(map_path, game.SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.ladder_list = tile_map.sprite_lists["Ladders"]
        self.moving_sprites_list = tile_map.sprite_lists["Moving Platforms"]
        self.background_list = tile_map.sprite_lists["Background"]
        self.goal_list = tile_map.sprite_lists["Goal"]

        # Create player sprite
        self.player_sprite = Player(self.ladder_list, hit_box_algorithm="Simple")

        # Create enemy sprite
        from newentities import Enemy
        self.enemy_sprite = Enemy("robot", "robot")
        # Add to enemy sprite list
        self.enemy_list.append(self.enemy_sprite)

        # Set player location
        grid_x = 1
        grid_y = 1
        self.player_sprite.center_x = game.SPRITE_SIZE * grid_x + game.SPRITE_SIZE / 2
        self.player_sprite.center_y = game.SPRITE_SIZE * grid_y + game.SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list.append(self.player_sprite)

        damping = game.DEFAULT_DAMPING

        # Set the gravity. (0, 0) is good for outer space and top-down.
        gravity = (0, -game.GRAVITY)

        # Create the physics engine
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity)

        def wall_hit_handler(bullet_sprite, _wall_sprite, _arbiter, _space, _data):
            """ Called for bullet/wall collision """
            bullet_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler("bullet", "wall", post_handler=wall_hit_handler)

        def item_hit_handler(bullet_sprite, item_sprite, _arbiter, _space, _data):
            """ Called for bullet/item collision """
            bullet_sprite.remove_from_sprite_lists()
            item_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler("bullet", "item", post_handler=item_hit_handler)

        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=game.PLAYER_FRICTION,
                                       mass=game.PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=game.PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=game.PLAYER_MAX_VERTICAL_SPEED)

        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=game.WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        # Create the items
        self.physics_engine.add_sprite_list(self.item_list,
                                            friction=game.DYNAMIC_ITEM_FRICTION,
                                            collision_type="item")

        # Add kinematic sprites
        self.physics_engine.add_sprite_list(self.moving_sprites_list,
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC)
        
        # Add the enemies to the physics engine
        for enemy in self.enemy_list:
            self.physics_engine.add_sprite(enemy, friction=0.6, mass=2.0, moment=arcade.PymunkPhysicsEngine.MOMENT_INF)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.SPACE:
            # Check if the player can jump
            if self.physics_engine.is_on_ground(self.player_sprite) or self.player_sprite.jump_count < 1:
                impulse = (0, game.PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                self.player_sprite.jump_count += 1  # Increment jump count
        elif key == arcade.key.ESCAPE:
            # Pass the current view to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.SPACE:
            self.space_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """

        bullet = arcade.SpriteSolidColor(20, 5, arcade.color.DARK_RED)
        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.position = self.player_sprite.position

        dest_x = x
        dest_y = y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        # Use angle to spawn bullet away from player in proper direction
        bullet.center_x += size * math.cos(angle)
        bullet.center_y += size * math.sin(angle)

        # Set angle of bullet
        bullet.angle = math.degrees(angle)

        bullet_gravity = (0, -game.BULLET_GRAVITY)

        # Add the sprite. This needs to be done AFTER setting the fields above.
        self.physics_engine.add_sprite(bullet,
                                       mass=game.BULLET_MASS,
                                       damping=1.0,
                                       friction=0.6,
                                       collision_type="bullet",
                                       gravity=bullet_gravity,
                                       elasticity=0.9)

        # Set velocity of bullet
        speed = 5000  # Adjust this value to change the speed of the bullet
        velocity = (speed * math.cos(angle), speed * math.sin(angle))
        self.physics_engine.set_velocity(bullet, velocity)

    def center_camera_to_player(self):

        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
        self.camera.viewport_height / 2
        )

        if screen_center_x < 0:
           screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""
        if self.display_timer < 0:

            self.show_instructions = not self.show_instructions

            self.display_timer = 1.0

        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        if is_on_ground:
            self.player_sprite.jump_count = 0  # Reset jump count when on the ground

        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
    
            if is_on_ground or self.player_sprite.is_on_ladder:
                force = (-game.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-game.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            if is_on_ground or self.player_sprite.is_on_ladder:
                force = (game.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (game.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.up_pressed and not self.down_pressed:
            # Create a force to move up the ladder
            if self.player_sprite.is_on_ladder:
                force = (0, game.PLAYER_CLIMB_FORCE)  # Use the new climbing force constant
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.down_pressed and not self.up_pressed:
            # Create a force to move down the ladder
            if self.player_sprite.is_on_ladder:
                force = (0, -game.PLAYER_CLIMB_FORCE)  # Use the new climbing force constant
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # Move items in the physics engine
        self.physics_engine.step()

        for moving_sprite in self.moving_sprites_list:
            if moving_sprite.boundary_right and \
                    moving_sprite.change_x > 0 and \
                    moving_sprite.right > moving_sprite.boundary_right:
                moving_sprite.change_x *= -1
            elif moving_sprite.boundary_left and \
                    moving_sprite.change_x < 0 and \
                    moving_sprite.left > moving_sprite.boundary_left:
                moving_sprite.change_x *= -1
            if moving_sprite.boundary_top and \
                    moving_sprite.change_y > 0 and \
                    moving_sprite.top > moving_sprite.boundary_top:
                moving_sprite.change_y *= -1
            elif moving_sprite.boundary_bottom and \
                    moving_sprite.change_y < 0 and \
                    moving_sprite.bottom < moving_sprite.boundary_bottom:
                moving_sprite.change_y *= -1

            velocity = (moving_sprite.change_x * 1 / delta_time, moving_sprite.change_y * 1 / delta_time)
            self.physics_engine.set_velocity(moving_sprite, velocity)

        self.center_camera_to_player()

        # Check if player reached the goal
        if arcade.check_for_collision_with_list(self.player_sprite, self.goal_list):
            self.level += 1
            self.setup()

    def on_draw(self):
        """ Draw everything """
        self.background_list.draw()
        self.camera.use()
        self.clear()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.moving_sprites_list.draw()
        self.bullet_list.draw()
        self.item_list.draw()
        self.goal_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
    