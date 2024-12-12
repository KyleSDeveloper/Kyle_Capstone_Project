import arcade

class Entity(arcade.Sprite):
    """ Base class for all entities in the game """
    def __init__(self, image, scale, hit_box_algorithm="Simple"):
        super().__init__(image, scale, hit_box_algorithm=hit_box_algorithm)
        self.change_x = 0
        self.change_y = 0
        self.boundary_left = None
        self.boundary_right = None
        self.boundary_top = None
        self.boundary_bottom = None
        self.dead = False

    def update(self):
        """ Update the entity's position and handle boundaries """
        if not self.dead:
            self.center_x += self.change_x
            self.center_y += self.change_y

            # Reverse direction if we hit the boundaries
            if self.boundary_left is not None and self.center_x < self.boundary_left:
                self.change_x *= -1
            if self.boundary_right is not None and self.center_x > self.boundary_right:
                self.change_x *= -1
            if self.boundary_top is not None and self.center_y > self.boundary_top:
                self.change_y *= -1
            if self.boundary_bottom is not None and self.center_y < self.boundary_bottom:
                self.change_y *= -1

    def kill(self):
        """ Mark the entity as dead """
        self.dead = True