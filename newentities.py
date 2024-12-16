import arcade
import constants as game

class Entity(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        # Default to facing right
        self.facing_direction = game.RIGHT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = game.SPRITE_SCALING_PLAYER
        self.character_face_direction = game.RIGHT_FACING

        main_path = f":resources:images/animated_characters/{name_folder}/{name_file}"

        # Load textures for different actions
        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")
        self.walk_textures = [arcade.load_texture_pair(f"{main_path}_walk{i}.png") for i in range(8)]
        self.climbing_textures = [arcade.load_texture(f"{main_path}_climb0.png"), arcade.load_texture(f"{main_path}_climb1.png")]

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        self.character_face_direction = game.RIGHT_FACING

        self.hit_box = self.texture.hit_box_points

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

class Enemy(Entity):
    def __init__(self, name_folder, name_file):

        # Setup parent class
        super().__init__(name_folder, name_file)

        self.should_update_walk = 0
        self.health = 0

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.facing_direction == game.RIGHT_FACING:
            self.facing_direction = game.LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == game.LEFT_FACING:
            self.facing_direction = game.RIGHT_FACING

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Walking animation
        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1


class RobotEnemy(Enemy):
    def __init__(self):

        # Set up parent class
        super().__init__("robot", "robot")

        self.health = 100


