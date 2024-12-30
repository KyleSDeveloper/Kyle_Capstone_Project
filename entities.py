import arcade
import constants as game

class Entity(arcade.Sprite):
    """ Player Sprite """
    def __init__(self, name_folder, name_file, ladder_list=None, hit_box_algorithm=None):
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

        # Ladder related attributes
        self.ladder_list = ladder_list
        self.is_on_ladder = False

       

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle being moved by the pymunk engine """
        if dx < -game.DEAD_ZONE and self.character_face_direction == game.RIGHT_FACING:
            self.character_face_direction = game.LEFT_FACING
        elif dx > game.DEAD_ZONE and self.character_face_direction == game.LEFT_FACING:
            self.character_face_direction = game.RIGHT_FACING

    
        is_on_ground = physics_engine.is_on_ground(self)

        if self.ladder_list and len(arcade.check_for_collision_with_list(self, self.ladder_list)) > 0:
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

        #  odometer for how far we've moved
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
        super().__init__("male_person", "malePerson", ladder_list, hit_box_algorithm)
        


class Enemy(Entity):
    def __init__(self, name_folder, name_file, platform_list):
        super().__init__(name_folder, name_file)
        self.speed = 100  # speed (adjust as needed)
        self.chase_range = 600  # chase range
        self.boundary_left = None
        self.boundary_right = None
        self.change_x = 0
        self.change_y = 0
        self.attack_range = 100  
        self.attack_cooldown = 1.0  
        self.time_since_last_attack = 0
        self.animation_timer = 0  # Timer to control animation speed
        self.platform_list = platform_list

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()  # Remove the enemy from the game

    
    def is_ground_ahead(self):
        """ Check if there is ground in front of the enemy """
        direction = 1 if self.change_x > 0 else -1
        front_x = self.center_x + (self.width / 2 * direction)
        front_y = self.center_y - self.height / 2  

        # Create a dummy sprite to check collision
        check_sprite = arcade.Sprite()
        check_sprite.center_x = front_x
        check_sprite.center_y = front_y
        check_sprite.width = 1  
        check_sprite.height = self.height  

        # Check if there's any platform under the new position
        collisions = arcade.check_for_collision_with_list(check_sprite, self.platform_list)
        return len(collisions) > 0

    def update(self, delta_time, player_sprite, physics_engine, bullet_list):

        # Chase the player if within range
        dx = player_sprite.center_x - self.center_x
        dy = player_sprite.center_y - self.center_y
        distance = (dx**2 + dy**2)**0.5 

        if distance < self.chase_range:
            if distance != 0:
                dx /= distance
                dy /= distance
            self.change_x = dx * self.speed
            self.change_y = 0  # Enemies don't jump

            if self.is_ground_ahead():
                self.change_x = dx * self.speed
            else:
                self.change_x = 0  # Stop if there's no ground ahead

        else:
            self.change_x = 0
            self.change_y = 0

        # Apply velocity to the enemy using the physics engine
        velocity = (self.change_x, self.change_y)
        physics_engine.set_velocity(self, velocity)

        # Check for boundaries and reverse direction if needed
        if self.boundary_left is not None and self.center_x < self.boundary_left:
            self.change_x *= -1
        if self.boundary_right is not None and self.center_x > self.boundary_right:
            self.change_x *= -1

        # Check for collisions with projectiles
        for bullet in bullet_list:
            if arcade.check_for_collision(self, bullet):
                self.take_damage(self.default_damage)  # Use default damage value
                bullet.kill()  # Remove the bullet

        # Update the enemy's animation
        self.update_animation(delta_time)

    def update_animation(self, delta_time):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == game.RIGHT_FACING:
            self.character_face_direction = game.RIGHT_FACING
        elif self.change_x > 0 and self.character_face_direction == game.LEFT_FACING:
            self.character_face_direction = game.LEFT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.animation_timer += delta_time
        if self.animation_timer > 0.1:  # Adjust this value to control animation speed
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
            self.animation_timer = 0

class RobotEnemy(Enemy):
    def __init__(self, platform_list):
        super().__init__("robot", "robot", platform_list)
        self.health = 50
        self.default_damage = 10

class SuperRobot(RobotEnemy):
    def __init__(self, platform_list):
        super().__init__(platform_list)
        self.scale = 2.0  # Make the SuperRobot twice as big
        self.health = 1000  # Increase health to make it stronger
        self.default_damage = 30  # Increase damage to make it stronger






