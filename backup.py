import math
from typing import Optional
import arcade
import constants as game



class EnemySprite(arcade.Sprite):
    """ Enemy Sprite """
    def __init__(self, image, dead_image, scale):
        super().__init__(image, scale)
        self.change_x = -game.ENEMY_MOVE_SPEED
        self.boundary_left = None
        self.boundary_right = None
        self.dead = False
        self.dead_texture = arcade.load_texture(dead_image)
        self.original_texture = arcade.load_texture(image)  # Ensure original_texture is loaded correctly

    def update(self):
        """ Move the enemy """
        if not self.dead:
            self.center_x += self.change_x

            # Reverse direction if we hit the boundaries
            if self.boundary_left is not None and self.center_x < self.boundary_left:
                self.change_x *= -1
                if isinstance(self.original_texture.name, str):  # Use 'name' instead of 'image'
                    self.texture = arcade.load_texture(self.original_texture.name, flipped_horizontally=True)
                else:
                    print("Error: original_texture.name is not a valid path string")
            if self.boundary_right is not None and self.center_x > self.boundary_right:
                self.change_x *= -1
                self.texture = self.original_texture
        else:
            self.texture = self.dead_texture

    def kill(self):
        """ Mark the enemy as dead """
        self.dead = True

class PlayerSprite(arcade.Sprite):
    """ Player Sprite """
    def __init__(self,
                 ladder_list: arcade.SpriteList,
                 hit_box_algorithm):
        """ Init """
    
        super().__init__()

        # Set our scale
        self.scale = game.SPRITE_SCALING_PLAYER

        main_path = ":resources:images/animated_characters/female_person/femalePerson"

        # Load textures for idle standing
        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png",
                                                          hit_box_algorithm=hit_box_algorithm)
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

        # Default to face-right
        self.character_face_direction = game.RIGHT_FACING

        # Index of our current texture
        self.cur_texture = 0

        # How far have we traveled horizontally since changing the texture
        self.x_odometer = 0
        self.y_odometer = 0

        self.ladder_list = ladder_list
        self.is_on_ladder = False

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle being moved by the pymunk engine """
        # Figure out if we need to face left or right
        if dx < -game.DEAD_ZONE and self.character_face_direction == game.RIGHT_FACING:
            self.character_face_direction = game.LEFT_FACING
        elif dx > game.DEAD_ZONE and self.character_face_direction == game.LEFT_FACING:
            self.character_face_direction = game.RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Are we on a ladder?
        if len(arcade.check_for_collision_with_list(self, self.ladder_list)) > 0:
            if not self.is_on_ladder:
                self.is_on_ladder = True
                self.pymunk.gravity = (0, 0)
                self.pymunk.damping = 0.0001
                self.pymunk.max_vertical_velocity = game.PLAYER_MAX_HORIZONTAL_SPEED
        else:
            if self.is_on_ladder:
                self.pymunk.damping = 1.0
                self.pymunk.max_vertical_velocity = game.PLAYER_MAX_VERTICAL_SPEED
                self.is_on_ladder = False
                self.pymunk.gravity = None

        # Add to the odometer how far we've moved
        self.x_odometer += dx
        self.y_odometer += dy

        if self.is_on_ladder and not is_on_ground:
            # Have we moved far enough to change the texture?
            if abs(self.y_odometer) > game.DISTANCE_TO_CHANGE_TEXTURE:

                # Reset the odometer
                self.y_odometer = 0

                # Advance the walking animation
                self.cur_texture += 1

            if self.cur_texture > 1:
                self.cur_texture = 0
            self.texture = self.climbing_textures[self.cur_texture]
            return

        # Jumping animation
        if not is_on_ground:
            if dy > game.DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -game.DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return

        # Idle animation
        if abs(dx) <= game.DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > game.DISTANCE_TO_CHANGE_TEXTURE:

            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class BulletSprite(arcade.SpriteSolidColor):
    """ Bullet Sprite """
    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle when the sprite is moved by the physics engine. """
        # If the bullet falls below the screen, remove it
        if self.center_y < -100:
            self.remove_from_sprite_lists()

class GameWindow(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title):
        """ Create the variables """
        # Init the parent class
        super().__init__(width, height, title)
        
        # Player sprite
        self.player_sprite: Optional[PlayerSprite] = None
        self.camera = None

        # Sprite lists we need
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.moving_sprites_list: Optional[arcade.SpriteList] = None
        self.ladder_list: Optional[arcade.SpriteList] = None
        self.enemy_list = arcade.SpriteList()

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

        # Physics engine
        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None

        # Set background color
        arcade.set_background_color(arcade.color.SILVER_LAKE_BLUE)

    def setup(self):
        """ Set up everything with the game """
                # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Add enemies
        enemy = EnemySprite("assets/images/Platformer Pack Redux (360 assets) (1)/PNG/Enemies/fly.png", 
                            "assets/images/Platformer Pack Redux (360 assets) (1)/PNG/Enemies/fly_move.png", 
                            scale=0.5)
        enemy.center_x = 300
        enemy.center_y = 250
        enemy.boundary_left = 100
        enemy.boundary_right = 500
        self.enemy_list.append(enemy)


        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        

        # Map name
        map_name = "assets/images/level_01.json"

        # Load in TileMap
        tile_map = arcade.load_tilemap(map_name, game.SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.ladder_list = tile_map.sprite_lists["Ladders"]
        self.moving_sprites_list = tile_map.sprite_lists["Moving Platforms"]
        self.background_list = tile_map.sprite_lists["Background"]
        self.goal_list = tile_map.sprite_lists["Goal"]

        # Create player sprite
        self.player_sprite = PlayerSprite(self.ladder_list, hit_box_algorithm="Detailed")

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
            """ Called for bullet/wall collision """
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

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            self.up_pressed = True
            # find out if player is standing on ground, and not on a ladder
            if self.physics_engine.is_on_ground(self.player_sprite) \
                    and not self.player_sprite.is_on_ladder:
                # She is! Go ahead and jump
                impulse = (0, game.PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        if key == arcade.key.SPACE:
            for enemy in self.enemy_list:
                enemy.kill()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """

        bullet = BulletSprite(20, 5, arcade.color.DARK_YELLOW)
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

        # What is the 1/2 size of this sprite, so we can figure out how far
        # away to spawn the bullet
        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        # Use angle to to spawn bullet away from player in proper direction
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

        # Add force to bullet
        force = (game.BULLET_MOVE_FORCE, 0)
        self.physics_engine.apply_force(bullet, force)

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

        # Move the player with the physics engine
        self.physics_engine.update()



        # Position the camera

        self.center_camera_to_player()

    def player_die(self):
        """ Handle the player's death """
        print("Player has died!")
        self.close()

    def on_update(self, delta_time):
        """ Movement and game logic """
        
        self.enemy_list.update()
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
            # Create a force to the left. Apply it.
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
            # Create a force to the right. Apply it.
            if self.player_sprite.is_on_ladder:
                force = (0, game.PLAYER_MOVE_FORCE_ON_GROUND)
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.down_pressed and not self.up_pressed:
            # Create a force to the right. Apply it.
            if self.player_sprite.is_on_ladder:
                force = (0, -game.PLAYER_MOVE_FORCE_ON_GROUND)
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0)

        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # Move items in the physics engine
        self.physics_engine.step()

        

        # Check for collisions
        if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list):
            self.player_die() 
        if arcade.check_for_collision_with_list(self.player_sprite, self.goal_list):
            self.congratulate_player()

        # For each moving sprite, see if we've reached a boundary and need to
        # reverse course.
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

        # Position the camera
        self.center_camera_to_player()

    def congratulate_player(self):
        print("Congratulations! You've passed the level!")
        self.close()

    def on_draw(self):
        """ Draw everything """
                # Activate our Camera
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

def main():
    """ Main function """
    window = GameWindow(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, game.SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()