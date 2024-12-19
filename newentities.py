import arcade
import constants as game

class Entity(arcade.Sprite):
    """ Player Sprite """
    def __init__(self, name_folder, name_file):
        """ Init """
        # parent initialize
        super().__init__()

        # Set our scale
        self.scale = game.SPRITE_SCALING_PLAYER

        main_path = f":resources:images/animated_characters/{name_folder}/{name_file}"

        # Load textures for different actions
        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")
        self.walk_textures = [arcade.load_texture_pair(f"{main_path}_walk{i}.png") for i in range(8)]
        self.climbing_textures = [arcade.load_texture(f"{main_path}_climb0.png"), arcade.load_texture(f"{main_path}_climb1.png")]

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

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle being moved by the pymunk engine """
        # Figure out if we need to face left or right
        if dx < -game.DEAD_ZONE and self.character_face_direction == game.RIGHT_FACING:
            self.character_face_direction = game.LEFT_FACING
        elif dx > game.DEAD_ZONE and self.character_face_direction == game.LEFT_FACING:
            self.character_face_direction = game.RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx

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

        if abs(self.x_odometer) > game.DISTANCE_TO_CHANGE_TEXTURE:

            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class Player(Entity):
    """Player Sprite class."""
    def __init__(self, ladder_list: arcade.SpriteList, hit_box_algorithm):
        super().__init__("male_person", "malePerson")

        self.ladder_list = ladder_list
        self.is_on_ladder = False
        self.health = 100

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

class Enemy(Entity):
    def __init__(self, name_folder, name_file):
        super().__init__(name_folder, name_file)
        self.boundary_left = None
        self.boundary_right = None
        self.change_x = 0
        self.attack_range = 100  # Example attack range
        self.attack_cooldown = 1.0  # Example cooldown time in seconds
        self.time_since_last_attack = 0

    def follow_player(self, player_sprite):
        if self.center_x < player_sprite.center_x:
            self.change_x = 1
        elif self.center_x > player_sprite.center_x:
            self.change_x = -1
        else:
            self.change_x = 0

    def attack_player(self, player_sprite):
        if abs(self.center_x - player_sprite.center_x) < self.attack_range:
            if self.time_since_last_attack >= self.attack_cooldown:
                # Perform attack (e.g., reduce player health)
                player_sprite.health -= 10  # Example damage value
                self.time_since_last_attack = 0

    def update(self, delta_time, player_sprite):
        # Follow the player
        self.follow_player(player_sprite)

        # Move the enemy
        self.center_x += self.change_x

        # Check for boundaries and reverse direction if needed
        if self.boundary_left is not None and self.center_x < self.boundary_left:
            self.change_x *= -1
        if self.boundary_right is not None and self.center_x > self.boundary_right:
            self.change_x *= -1

        # Attack the player if in range
        self.attack_player(player_sprite)

        # Update the time since the last attack
        self.time_since_last_attack += delta_time

    def update_animation(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == game.RIGHT_FACING:
            self.character_face_direction = game.LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == game.LEFT_FACING:
            self.character_face_direction = game.RIGHT_FACING

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1


class RobotEnemy(Enemy):
    def __init__(self):

        # Set up parent class
        super().__init__("robot", "robot")

        self.health = 100


