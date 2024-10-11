import pygame

class Player(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        super().__init__()
        self.direction = 'down'
        self.state = 'idle'
        self.image = animations[self.direction][self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_count = 0
        self.speed = 1
        self.facing_right = True  # Initially facing right
        self.attacking = False
        self.picking_up = False

    def move(self, dx, dy):
        if not self.attacking and not self.picking_up:  # Prevent movement during attack or pick-up
            if dx != 0 or dy != 0:
                self.state = 'walk'
                if dx != 0:
                    self.direction = 'right' if dx > 0 else 'left'
                    self.facing_right = dx > 0  # Update facing direction
                else:
                    self.direction = 'down' if dy > 0 else 'up'
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
            else:
                self.state = 'idle'

    def attack(self):
        self.state = 'attack'
        self.attacking = True
        self.animation_count = 0

    def pick_up(self):
        self.state = 'pickup'
        self.picking_up = True
        self.animation_count = 0

    # Move the sprite based on user keypresses
def update(self, pressed_keys):
    if pressed_keys[K_UP]:
        self.rect.move_ip(0, -5)
    if pressed_keys[K_DOWN]:
        self.rect.move_ip(0, 5)
    if pressed_keys[K_LEFT]:
        self.rect.move_ip(-5, 0)
    if pressed_keys[K_RIGHT]:
        self.rect.move_ip(5, 0)
