import pygame
import os
import random
import csv
import json
import re
import runpy
import subprocess
import sys
import math
# import button

APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)

def resource_path(relative_path):
    direct_path = os.path.join(RESOURCE_DIR, relative_path)
    if os.path.exists(direct_path):
        return direct_path

    if relative_path.startswith(("img/", "img\\", "audio/", "audio\\")):
        asset_path = os.path.join(RESOURCE_DIR, "shooter_assets", relative_path)
        if os.path.exists(asset_path):
            return asset_path

    if re.fullmatch(r"level\d+_data\.csv", relative_path):
        level_path = os.path.join(RESOURCE_DIR, "levels", relative_path)
        if os.path.exists(level_path):
            return level_path

    return direct_path

def writable_path(relative_path):
    return os.path.join(APP_DIR, relative_path)

OVERRIDE_LEVELS_FILE = writable_path("edited_levels.json")

def load_level_overrides():
    if not os.path.exists(OVERRIDE_LEVELS_FILE):
        return {}
    try:
        with open(OVERRIDE_LEVELS_FILE, "r") as jsonfile:
            return json.load(jsonfile)
    except (json.JSONDecodeError, OSError):
        return {}

def level_file_path(level_number):
    writable_level = writable_path(f"level{level_number}_data.csv")
    if os.path.exists(writable_level):
        return writable_level
    return resource_path(f"level{level_number}_data.csv")

def available_levels():
    levels = set()
    search_folders = (
        APP_DIR,
        os.path.join(APP_DIR, "levels"),
        RESOURCE_DIR,
        os.path.join(RESOURCE_DIR, "levels"),
    )
    for folder in search_folders:
        if os.path.isdir(folder):
            for filename in os.listdir(folder):
                match = re.fullmatch(r"level(\d+)_data\.csv", filename)
                if match:
                    levels.add(int(match.group(1)))
    return sorted(levels)

if "--editor" in sys.argv:
    runpy.run_path(resource_path("level_editor.py"), run_name="__main__")
    sys.exit()

pygame.init()

SCREEN_WIDTH= 500 # pixels
SCREEN_HEIGHT= int(SCREEN_WIDTH*0.8) # int becux normallly it would give float value 
 
screen= pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

#set frame rate
clock=pygame.time.Clock()
FPS=60 # 60 frames per second

# game variables
GRAVITY = 0.75
SCROLL_THRESH = 200 #200 PIXELS
# PLAYER_BULLET_SPEED = 14
# ENEMY_BULLET_SPEED = 4
# PLAYER_BULLET_DAMAGE = 50
# ENEMY_BULLET_DAMAGE = 20
TILE_SIZE = 40
LEVEL = 1
ROWS = 16
COLUMNS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS # comnverts teh whole window to individual tiles
TILE_TYPES = 21  # 21 tiles types to make the new levels 
MAX_LEVEL = max(available_levels() or [3])
scroll_thresh = 0
bg_scroll = 0
screen_scroll = 0
start_game = False
start_intro = False

# Define players actions variables
moving_left=False
moving_right=False
shoot = False
grenade = False
grenade_thrown = False


# load musc and sounds
pygame.mixer.music.load(resource_path('audio/music2.mp3'))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000) # 5000 milli secounds
jump_fx = pygame.mixer.Sound(resource_path('audio/jump.wav'))
jump_fx.set_volume(0.5)
shoot_fx = pygame.mixer.Sound(resource_path('audio/shot.wav'))
shoot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound(resource_path('audio/grenade.wav'))
grenade_fx.set_volume(0.5)

# load images
# button img
start_img = pygame.image.load(resource_path('img/start_btn.png')).convert_alpha()
exit_img = pygame.image.load(resource_path('img/exit_btn.png')).convert_alpha()
restart_img = pygame.image.load(resource_path('img/restart_btn.png')).convert_alpha()

# bg
pinel_img = pygame.image.load(resource_path('img/Background/pine1.png')).convert_alpha()
pine2_img = pygame.image.load(resource_path('img/Background/pine2.png')).convert_alpha()
mountain_img = pygame.image.load(resource_path('img/Background/mountain.png')).convert_alpha()
sky_img = pygame.image.load(resource_path('img/Background/sky_cloud.png')).convert_alpha()

def scale_to_screen_width(img):
    scale = SCREEN_WIDTH / img.get_width()
    return pygame.transform.smoothscale(img, (SCREEN_WIDTH, int(img.get_height() * scale)))

sky_img = pygame.transform.smoothscale(sky_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
mountain_img = scale_to_screen_width(mountain_img)
pinel_img = scale_to_screen_width(pinel_img)
pine2_img = scale_to_screen_width(pine2_img)

# store tiles in a list
img_list = [] # as 21 tiles so iterate thro each and put in list and load
for x in range(TILE_TYPES):
    img = pygame.image.load(resource_path(f'img/Tile/{x}.png'))
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# bullets
bullet_img = pygame.image.load(resource_path('img/icons/bullet.png')).convert_alpha()
# convert_alpha() : format that pygame uses to handle transparency in images so that when we load the bullet img it would have a transparent background instead of a white background which is the default background color for images in pygame and this would make the bullet look better when we draw it on the screen later on in the game
# grenade
grenade_img = pygame.image.load(resource_path('img/icons/grenade.png')).convert_alpha()
# pick up boxes
health_box_img = pygame.image.load(resource_path('img/icons/health_box.png')).convert_alpha()
ammo_box_img = pygame.image.load(resource_path('img/icons/ammo_box.png')).convert_alpha()
grenade_box_img = pygame.image.load(resource_path('img/icons/grenade_box.png')).convert_alpha()
item_boxes= {
    'Health' : health_box_img,
    'Ammo' : ammo_box_img,
    'Grenade': grenade_box_img
}
#define colors
BG=(135, 206, 235) # sky blue fallback background
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0, 255,0)
BLACK = (0,0,0)
PINK = (235, 65, 54)

# define fonts
font = pygame.font.SysFont('Future',  30)
font_small = pygame.font.SysFont('Arial', 16, bold=True)

# NEW UPDATED DISPLAYS FOR BULLETS/ HEALT_BAR / GRENEADES
#  create img from text  -- as python doesnot displays text ono screen in pygame
def draw_text(text, font, texct_col, x, y):
    img = font.render(text, True, texct_col) # render: draw the current frame/state to the screen 
    screen.blit(img, (x, y))

def draw_hud_panel(x, y, width, height):
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 24, 28, 185), panel.get_rect(), border_radius=8)
    pygame.draw.rect(panel, (255, 255, 255, 35), panel.get_rect(), 1, border_radius=8)
    screen.blit(panel, (x, y))

# function to reset level
def reset_level():
    enemy_group.empty() # deleetes teh instances all of them
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    
    #  create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLUMNS # THIS IS FOR 1 ROW    # -1 : means nothing is there in that space
        data.append(r)
    return data


def draw_icon_counter(icon, count, x, y):
    draw_hud_panel(x, y, 72, 28)
    icon_scale = 0.7
    icon_img = pygame.transform.smoothscale(
        icon,
        (int(icon.get_width() * icon_scale), int(icon.get_height() * icon_scale))
    )
    screen.blit(icon_img, (x + 10, y + (28 - icon_img.get_height()) // 2))
    count_img = font_small.render(str(count), True, WHITE)
    screen.blit(count_img, (x + 45, y + (28 - count_img.get_height()) // 2))

def draw_layer(img, scroll, y):
    width = img.get_width()
    offset = int(scroll % width)
    for x in range(-1, (SCREEN_WIDTH // width) + 3):
        screen.blit(img, ((x * width) - offset, y))

# update bg -- refresh bg
def draw_bg():
    screen.fill(BG) # u need to call it inside the while loop so it works
    draw_layer(sky_img, bg_scroll * 0.15, 0)
    draw_layer(mountain_img, bg_scroll * 0.35, SCREEN_HEIGHT - mountain_img.get_height() - 110)
    draw_layer(pinel_img, bg_scroll * 0.6, SCREEN_HEIGHT - pinel_img.get_height() - 55)
    draw_layer(pine2_img, bg_scroll * 0.85, SCREEN_HEIGHT - pine2_img.get_height())
    # pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300)) # this would draw a line on the screen at the bottom to represent the ground and we would use this line to check for collision with the player later on in the game

class Soldier(pygame.sprite.Sprite): # this class would be used to create player characters in the game, we are inheriting from pygame.sprite.Sprite which is a built in class in pygame that provides basic functionality for creating sprites (game objects) and also provides methods for handling collisions and other interactions between sprites, by inheriting from this class we can easily create our own custom sprites for our game
    def __init__(self, char_type , x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo # track of the bullets like 20 bulletss per player
        self.start_ammo = ammo
        self.shoot_cooldown = 0 # rate of fire
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health # for health bar
        self.direction = 1 # 1: right, -1: left
        self.velocity_y = 0 # for jump velocity
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = [] # this would be used to store the different animations for the player (like idle, run, jump, etc) and we would load the images for these animations in this list and then we can use this list to draw the animations on the screen later on in the game
        self.frame_index = 0 # so animation is in the very 1st fram
        self.action = 0 # 0: idle, 1: run, 2: jump
        self.update_time = pygame.time.get_ticks() # for time tracking
        self.death_animation_finished = False
        self.vanish_started = False
        self.vanish_counter = 0
        self.vanish_duration = 48
        self.vanished = False
        
        # create ai specific var
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 220, 80) # rect x,y,width,height -- rect fro enemy if player in this rect then enemy shoots 
        self.idling = False
        self.idling_counter = 0
        self.patrol_distance = random.randint(TILE_SIZE * 2, TILE_SIZE * 5)
        self.ai_decision_counter = random.randint(45, 120)

        # load all img fro the player
        animation_types = ['Idle', 'Run', 'Jump', 'Death'] # this is the list of different animation types for the player and we would use this list to load the images for these animations in the animation_list
        for animation in animation_types:

            temp_list = [] # this would be used to store the images for the idle animation temporarily before we load them into the animation_list
            
            # count no. of files in folder : how many items are in each folder so that the next loop number is correct & acc to it
            numb_of_frmaes = len(os.listdir(resource_path(f'img/{self.char_type}/{animation}')))  # list dir : list in directory
            
            for i in range(numb_of_frmaes):
                # str formating method to load img for diff char
                img= pygame.image.load(resource_path(f'img/{self.char_type}/{animation}/{i}.png')).convert_alpha() # load the char img
                img=pygame.transform.scale(img,(int(img.get_width()*scale) ,int(img.get_height()*scale)))
                temp_list.append(img) # store the img into the list        
            self.animation_list.append(temp_list) # store the idle animation list into the animation_list which is a list of lists and each list inside it would be for a different animation like idle, run, jump, etc
         

        # self.img makes it the instances variable so that we can access it in other methods of the class and also to draw it on the screen, if we just use img then it would be a local variable and we won't be able to access it outside of this method
        # self.image=pygame.transform.scale(img,(int(img.get_width()*scale) ,int(img.get_height()*scale)))   #need to increas ethe img size overall so call this so that it would scale the img to the new width and height we provide, here we are using the original width and height of the img and then multiplying it by a factor to make it bigger, for example if we want to make it 2 times bigger we can do img.get_width()*2 and img.get_height()*2  # img is too small so scale it up (make it bigger)
        
        self.image = self.animation_list[self.action][self.frame_index] # gives the img fro curr action from list of lists
        self.rect=self.image.get_rect() # takes size of img and creates boundary box around it
        # this rect would be used to move the char and also to check for collision with other objects in the game
        self.rect.center=(x,y) # position the rect based on x, y coordinates
        # its not the IMG that is moving its the RECT that is moving so we move the player using the rect with its speed meaning the scale is now the speed (speed=how many pixels to move the player now)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.char_type == "player" and self.alive == False and self.death_animation_finished and self.vanished == False:
            self.vanish_started = True
            self.vanish_counter += 1
            if self.vanish_counter >= self.vanish_duration:
                self.vanished = True
        #update cooldown
        if self.shoot_cooldown > 0 :
            self.shoot_cooldown -= 1 # decrease the cooldown by 1 every frame until it reaches 0 so that the player can shoot again after a certain amount of time has passed
        if self.is_drowning():
            self.health = 0
            self.check_alive()
    
    def move(self,moving_left, moving_right):
        #reset movement var
        screen_scroll = 0
        dx=0 # change in x
        dy=0 # change in y

        if moving_left:  # assign var if mov left or right is True
            dx = -self.speed # (-x axis) x coordinate is decreasing
            self.flip = True # flip the img when moving left
            self.direction = -1
        if moving_right:
            dx = self.speed # (+x axis) x coordinate is increasing
            self.flip = False
            self.direction = 1
        
        #jump
        if self.jump == True and self.in_air == False: 
            self.velocity_y = -11 # cuz top of screen is 0 and bottom is 600 so to move up we need to decrease the y coordinate and to move down we need to increase the y coordinate so for jump we need to decrease the y coordinate by a certain amount and then we would increase it again to bring the player back down
            self.jump = False # so players jumps once
            self.in_air = True 
        
        # apply gravity
        self.velocity_y += GRAVITY # increase the jump velocity over time
        if self.velocity_y > 10: # limit the jump velocity so that the player doesn't fall too fast
            self.velocity_y = 10
        dy += self.velocity_y # update the change in y by the jump velocity
        
        # check for collision :
        for tile in world.obstacle_list:
            # check collision in x Direction
            # use dx & dy such that before player moves it like checks 5 pixels when the player (scenerio) would move 
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # we need the rect box i-e around the player
                dx = 0 # this whole ould stop player from moving through the obstacles
                # if ai has hit the wall then make it turn acround
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in y Direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # we need the rect box i-e around the player
                #c heck if below the ground i-e jumping
                if self.velocity_y < 0: 
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground i-e falling
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    self.in_air = False # no longer in air so can jump again
                    dy = tile[1].top - self.rect.bottom

        # Temp Floor
        # if self.rect.bottom +dy > 300: # if the bottom of the rect is going to go below the floor line (y=300) then we need to stop the player from falling and set its position to be on the floor
        #     dy = 300 - self.rect.bottom # set the change in y to be the distance from the bottom of the rect to the floor line so that the player would be positioned on the floor line and not below it
        #     self.velocity_y = 0 # reset the jump velocity so that the player can jump again
        #     self.in_air = False # player is no longer in the air so it can jump again

        # check collision with water
        if self.is_drowning():
            self.health = 0 

        # check for collsion   with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False): #false: means kill
            level_complete = True 
    
        # check if fallen of the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type =='player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
        # update rect position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # update scroll base don players position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length *TILE_SIZE) - SCREEN_WIDTH) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete


    def shoot(self):
        if self.shoot_cooldown == 0 and (self.ammo > 0 or self.char_type == "enemy"):
            if self.char_type == "enemy":
                self.shoot_cooldown = 55
            else:
                self.shoot_cooldown = 18 # increase the value so taht player cant shoot too many bullets at a tiem ..but then we decrese this no. so that after few time player can shoot
            bullet = Bullet(self.rect.centerx +(0.59*self.rect.size[0]* self.direction) , self.rect.centery, self.direction, self.char_type) # this would create a bullet at the center of the player and in the direction the player is facing
            bullet_group.add(bullet) # add the bullet to the bullet group so that we can draw it on the screen and update its position later on in the game
            if self.char_type == "player":
                self.ammo -= 1 
            shoot_fx.play()

    def has_line_of_sight_to_player(self):
        if not self.vision.colliderect(player.rect):
            return False
        if (player.rect.centerx - self.rect.centerx) * self.direction < 0:
            return False
        for tile in world.obstacle_list:
            if tile[1].clipline(self.rect.center, player.rect.center):
                return False
        return True

    def should_turn_at_edge(self):
        if self.in_air:
            return False
        ahead_x = self.rect.centerx + self.direction * (self.width // 2 + 12)
        feet_y = self.rect.bottom + 3
        for tile in world.obstacle_list:
            if tile[1].collidepoint(ahead_x, feet_y):
                return False
        return True

    def is_drowning(self):
        for water in water_group:
            if self.rect.colliderect(water.rect):
                overlap = self.rect.clip(water.rect)
                feet_are_deep = self.rect.bottom > water.rect.top + (TILE_SIZE * 0.45)
                enough_horizontal_overlap = overlap.width > self.width * 0.35
                if feet_are_deep and enough_horizontal_overlap:
                    return True
        return False

    def ai(self):
        self.rect.x += screen_scroll
        self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

        if not self.alive or not player.alive:
            self.update_action(0 if self.alive else 3)
            return

        can_see_player = self.has_line_of_sight_to_player()
        if can_see_player:
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self.flip = self.direction == -1
            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
            self.update_action(0)
            self.shoot()
            return

        if not self.idling and random.randint(1, 180) == 1:
            self.idling = True
            self.idling_counter = 45
            self.update_action(0)
            return

        if self.idling:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False
            self.update_action(0)
            return

        self.ai_decision_counter -= 1
        if self.ai_decision_counter <= 0:
            choice = random.randint(1, 4)
            if choice == 1:
                self.idling = True
                self.idling_counter = random.randint(25, 70)
                self.update_action(0)
                self.ai_decision_counter = random.randint(45, 120)
                return
            if choice == 2:
                self.direction *= -1
                self.move_counter = 0
            self.patrol_distance = random.randint(TILE_SIZE * 2, TILE_SIZE * 5)
            self.ai_decision_counter = random.randint(45, 120)

        if self.should_turn_at_edge():
            self.direction *= -1
            self.move_counter = 0

        self.move(self.direction == -1, self.direction == 1)
        self.update_action(1)
        self.move_counter += 1
        self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

        if abs(self.move_counter) >= self.patrol_distance:
            self.direction *= -1
            self.move_counter = 0
        


    def update_animation(self): 
        # we need a timer when timer passes we flip to next img and thats how animation works and is semeless
        ANIMATION_COOLDOWN = 100  # 100 ms # timer so thsi scontrols the sppeed of animation
        #we need to know the time at beginning to knwo what time has passed so create  time at the instance is created 
        
        #update img dedpending upon curr frame
        self.image = self.animation_list[self.action][self.frame_index] # update img

        # check if anough time has passeed since last upd
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks() # reset timer
            self.frame_index += 1 # move to next frame   # as there r 5 img in list so when this vavr reaches 6 it gives error : so need to reet back to start
        # if animation has run out the reset back to start
        if self.frame_index >= len(self.animation_list[self.action]): # check if frame index has reached the end of the animation list
            if self.action == 3: # death action so frame index !=0  but stop when animation is doen once
                self.frame_index = len(self.animation_list[self.action]) - 1 # stop at the last frame of the death animation
                self.death_animation_finished = True
            else:
                self.frame_index = 0 # animation back to start
    

    
    def update_action(self, new_action):
        # check if the new action is different from the previous one
        if new_action != self.action: # if new action is diff form curr action then 
            self.action = new_action # update action
            # update animation settings
            self.frame_index = 0 # reset frame index to start of new animation
            self.update_time = pygame.time.get_ticks() # reset timer for new animation
            if new_action == 3:
                self.death_animation_finished = False


    def draw(self):
        if self.vanished:
            return
        if self.vanish_started:
            self.draw_whoosh_vanish()
            return
        # using the obj name toaccess the image, rect var form the class
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)  # x coordinate flips but False: mean that y coordinate remains the same no flip for it
        # pygame.draw.rect(screen, RED, self.rect,1) # makes boundary box around charc
        # this would draw the img on the screen at the position of rect
        # screen.blit(player2.image,player2.rect) instaed use self so that we can draw any player we want by calling the draw method of that player 

    def draw_whoosh_vanish(self):
        progress = min(1, self.vanish_counter / self.vanish_duration)
        eased = 1 - pow(1 - progress, 3)
        centre_x = self.rect.centerx
        centre_y = self.rect.centery - int(eased * 28)
        vanish_dir = -1 if self.flip else 1
        base_image = pygame.transform.flip(self.image, self.flip, False)

        for trail in range(3, 0, -1):
            trail_progress = max(0, progress - trail * 0.06)
            trail_eased = 1 - pow(1 - trail_progress, 3)
            trail_scale = max(0.16, 1 - trail_eased * 0.72)
            trail_alpha = max(0, int(95 * (1 - progress) / trail))
            trail_img = pygame.transform.smoothscale(
                base_image,
                (max(1, int(self.width * trail_scale)), max(1, int(self.height * trail_scale)))
            )
            trail_img.set_alpha(trail_alpha)
            trail_rect = trail_img.get_rect(center=(
                centre_x - vanish_dir * trail * 13,
                centre_y + trail * 5
            ))
            screen.blit(trail_img, trail_rect)

        alpha = max(0, int(255 * (1 - progress)))
        scale_x = max(0.12, 1 - eased * 0.78)
        scale_y = max(0.1, 1 - eased * 0.9)
        squash = 1 + math.sin(progress * math.pi) * 0.18
        image = pygame.transform.smoothscale(
            base_image,
            (max(1, int(self.width * scale_x * squash)), max(1, int(self.height * scale_y)))
        )
        image.set_alpha(alpha)
        rect = image.get_rect(center=(centre_x + int(vanish_dir * eased * 18), centre_y))
        screen.blit(image, rect)

        effect = pygame.Surface((190, 140), pygame.SRCALPHA)
        centre = (95, 70)
        for i in range(5):
            ring_progress = min(1, progress + i * 0.08)
            radius_x = int(18 + ring_progress * 70)
            radius_y = int(6 + ring_progress * 30)
            ring_alpha = int(165 * (1 - ring_progress))
            pygame.draw.ellipse(
                effect,
                (235, 250, 255, ring_alpha),
                (centre[0] - radius_x, centre[1] - radius_y, radius_x * 2, radius_y * 2),
                2
            )

        for i in range(7):
            y = 35 + i * 11
            length = 36 + i * 7
            x_offset = int(eased * 52) + i * 3
            alpha_line = max(0, int(170 * (1 - progress) - i * 8))
            start = (centre[0] - vanish_dir * (60 - x_offset), y)
            end = (start[0] + vanish_dir * length, y - 9)
            pygame.draw.line(effect, (245, 250, 255, alpha_line), start, end, 3)

        for i in range(10):
            angle = progress * math.pi * 2 + i * 0.65
            distance = 16 + eased * (28 + i * 2)
            spark_x = centre[0] + int(math.cos(angle) * distance)
            spark_y = centre[1] + int(math.sin(angle) * distance * 0.55)
            spark_alpha = max(0, int(210 * (1 - progress)))
            pygame.draw.circle(effect, (255, 242, 155, spark_alpha), (spark_x, spark_y), 2)

        screen.blit(effect, effect.get_rect(center=(centre_x, centre_y)))

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3) # Death action

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data): # this data is form csv file
        self.level_length = len(data[0])
        player = None
        health_bar = None
        # iterate thro each value in leveel data fiels -- gping thro rows
        for y , row in enumerate(data):
            # # in each row we are going thro each column/individual no. i-e the each tile
            for x, tile in enumerate(row):
                if tile >= 0: # process 0 or above -- dont process -1 as its nothing (empty space)
                    img = img_list[tile] # tile is a no. and it corresponds to an img
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE # tile size would chaneg with the screen size now
                    img_rect.y = y*TILE_SIZE
                    tile_data = (img, img_rect) # this has all inof about the individual tile
                    if tile >= 0 and tile <= 8: #1st 8 tiles are obstacles as in designed csv
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10: # this is water : downing : player.killed
                        # water
                        water = Water(img, x*TILE_SIZE, y*TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        # deccorations (grass/rocks)
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15 : # create player
                        player= Soldier("player",x*TILE_SIZE, y*TILE_SIZE, 1.3, 5, 20, 5)      # x,y=200 & scale=2 speed=5--how many pixels it gonna move
                        health_bar = HealthBar(10 , 10, player.health, player.health)
                    elif tile == 16:
                        enemy= Soldier("enemy",x*TILE_SIZE, y*TILE_SIZE, 1.3, 2, 20, 0)
                        enemy_group.add(enemy) # add the enemy to the enemy group so that we can draw it on the screen and update its position later on in the game
                    elif tile ==17: # create ammo box
                        item_box = ItemBox("Ammo",x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile ==18: # create grenade box
                        item_box = ItemBox("Grenade",x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile ==19: # create health box
                        item_box = ItemBox("Health",x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit
                        exit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        exit_group.add(exit)

        if player is None:
            raise ValueError("No player start tile (15) found in level data.")
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list: #blit : draw the img on the screen at the position of the rect
            tile[1].x += screen_scroll 
            screen.blit(tile[0], tile[1]) # tile[0] is the img and tile[1] is the rect


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) # this would position the decoration at the top of the tile and centered horizontally within the tile
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) # this would position the decoration at the top of the tile and centered horizontally within the tile
    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self) # inheriting methods from sprite class
        self.item_type = item_type 
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = ( x + TILE_SIZE // 2, y+(TILE_SIZE - self.image.get_height()))
    
    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if player has picked -- collision b/w player and item9)self:item_box
        if pygame.sprite.collide_rect(self, player): #--collision b/w item_box and player 
            # check kind of box?
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.width = 150
        self.height = 18

    def draw(self, health):
        #update with new health
        self.health = health
        # calcualte helath ratio
        ratio = max(0, min(self.health, self.max_health)) / self.max_health
        draw_hud_panel(self.x, self.y, self.width + 52, 28)

        label_img = font_small.render("HP", True, (225, 232, 226))
        screen.blit(label_img, (self.x + 10, self.y + (28 - label_img.get_height()) // 2))

        bar_x = self.x + 42
        bar_y = self.y + 8
        pygame.draw.rect(screen, (52, 61, 56), (bar_x, bar_y, self.width, self.height - 6), border_radius=6)
        pygame.draw.rect(screen, (84, 214, 124), (bar_x, bar_y, self.width * ratio, self.height - 6), border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, self.width, self.height - 6), 1, border_radius=6)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        pygame.sprite.Sprite.__init__(self) # inheriting methods from sprite class
        # Use per-owner tuning values directly to avoid reliance on commented-out globals
        if owner == "player":
            self.speed = 14
            self.damage = 50
        else:
            self.speed = 4
            self.damage = 20
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) #position of bullet would be at the center of the player when we shoot it
        self.direction = direction # direction of the bullet (1 : right, -1 : left)
        self.owner = owner
    
    def update(self):
        old_centerx = self.rect.centerx
        old_centery = self.rect.centery
        # move bullets
        self.rect.x += (self.direction * self.speed) + screen_scroll # update the x coordinate of the bullet based on its direction and speed
        hitbox_left = min(old_centerx, self.rect.centerx) - 8
        hitbox_top = min(old_centery, self.rect.centery) - 8
        hitbox_width = abs(self.rect.centerx - old_centerx) + 16
        hitbox_height = abs(self.rect.centery - old_centery) + 16
        bullet_hitbox = pygame.Rect(hitbox_left, hitbox_top, hitbox_width, hitbox_height)

        # check if bullets has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH: # if the right side of the bullet is less than 0 (off the left side of the screen) or if the left side of the bullet is greater than the screen width (off the right side of the screen) then we need to remove the bullet from the game
            self.kill() 
            return

        # check collision with char
        if self.owner == "player":
            for enemy in enemy_group:
                if enemy.alive and bullet_hitbox.colliderect(enemy.rect.inflate(20, 12)):
                    enemy.health -= self.damage
                    enemy.check_alive()
                    self.kill() # bullet disappears
                    return
        elif self.owner == "enemy":
            if player.alive and bullet_hitbox.colliderect(player.rect.inflate(8, 8)):
                player.health -= self.damage
                player.check_alive()
                self.kill() # bullet disappears
                return

        # check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                return

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self) # inheriting methods from sprite class
        self.timer = 100 # time before explosion
        self.velocity_y = -11 # initial jump velocity for grenade -- vertical speed
        self.speed = 7 # horizontal speed
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) #position of grenaade would be at the center of the player when we shoot it
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction # direction of the grenade (1 : right, -1 : left)
        
    def update(self):
        self.velocity_y += GRAVITY # apply gravity to the grenade
        if self.velocity_y > 10:
            self.velocity_y = 10
        dx = self.direction * self.speed # horizontal movement
        dy = self.velocity_y # vertical movement

        # check collison for level
        for tile in world.obstacle_list:
            # check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1  # reverse the direction of the grenade by multiplying it by -1 so that if it was moving to the right (direction = 1) it would now move to the left (direction = -1) and if it was moving to the left (direction = -1) it would now move to the right (direction = 1)
                dx = self.direction * self.speed # update the horizontal movement after changing direction
            # check for collision in y Direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # we need the rect box i-e around the player
                self.speed = 0
                # check if below the ground i-e thrown up 
                if self.velocity_y < 0: 
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground i-e thrown down 
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    dy = tile[1].top - self.rect.bottom

        # # check collision with floor:
        # if self.rect.bottom +dy > 300: # if the bottom of the rect is going to go below the floor line (y=300) then we need to stop the player from falling and set its position to be on the floor
        #     dy = 300 - self.rect.bottom # set the change in y to be the distance from the bottom of the rect to the floor line so that the player would be positioned on the floor line and not below it
        #     self.speed = 0 # when hits ground the grenades stops moving horixontally
        
        # # check collision with walls
        # if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH: # if the left side of the grenade is going to go off the left side of the screen or if the right side of the grenade is going to go off the right side of the screen then we need to reverse the direction of the grenade so that it bounces off the wall instead of going off the screen
        #     self.direction *= -1  # reverse the direction of the grenade by multiplying it by -1 so that if it was moving to the right (direction = 1) it would now move to the left (direction = -1) and if it was moving to the left (direction = -1) it would now move to the right (direction = 1)
        #     dx = self.direction * self.speed # update the horizontal movement after changing direction

        # update grenade posiiton
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # countdeon timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5) # create an explosion at the position of the grenade when it explodes and scale it down to 0.5 so that it looks better on the screen and not too big
            explosion_group.add(explosion) # add the explosion to the explosion group so that we can draw it on the screen and update its animation later on in the game
            
            # do damage to anyone that is nearby player + enemy
            # checking for distance not collision:
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                 abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2 :
                player.health -= 50
            
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                 abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2 :
                    enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self) # inheriting methods from sprite class
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(resource_path(f'img/explosion/exp{num}.png')).convert_alpha()
            img  = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) #position of grenaade would be at the center of the player when we shoot it
        self.counter = 0 # to keep track of how long the explosion has been on the screen
    
    def update(self):
        # scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4 # how fast the explosion animation plays
        # update explosion animation
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED: # if the counter has reached the explosion speed then we need to update the animation to the next frame
            self.counter = 0 # reset counter
            self.frame_index += 1 # move to the next frame in the explosion animation
            # if the animation has run out then we need to remove the explosion 
            if self.frame_index >= len(self.images): # if the frame index has reached the end of the explosion animation then we need to remove the explosion from the game
                self.kill() # remove explosion
            else:
                self.image = self.images[self.frame_index] # update the image of the explosion to the next frame in the animation

# create sprite groups
enemy_group = pygame.sprite.Group() # creates a blank group for enemies and we can add enemy sprites to this group when we create them and then we can draw all the enemies in this group on the screen by calling the draw method of the group and also we can update the position of all the enemies in this group by calling the update method of the group
bullet_group = pygame.sprite.Group() # creates a blank group for bullets and we can add bullet sprites to this group when we create them and then we can draw all the bullets in this group on the screen by calling the draw method of the group and also we can update the position of all the bullets in this group by calling the update method of the group # becuz this class is inherited form sprite so it can use draw / update methods   
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, image, scale):
        width  = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
         # draw button
        # Draw the button image at the button's position
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

class TextButton():
    def __init__(self, x, y, width, height, text, colour=(69, 123, 157)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.colour = colour
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        hover = self.rect.collidepoint(pos)
        colour = tuple(min(255, value + 24) for value in self.colour) if hover else self.colour

        pygame.draw.rect(surface, colour, self.rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=6)
        label = font_small.render(self.text, True, WHITE)
        surface.blit(label, label.get_rect(center=self.rect.center))

        if hover and mouse_down and self.clicked == False:
            action = True
            self.clicked = True
        if mouse_down == 0:
            self.clicked = False
        return action

def get_available_levels():
    return available_levels()

def load_level(level_number, clear_groups=True):
    global LEVEL, MAX_LEVEL, world_data, world, player, health_bar
    LEVEL = level_number
    available = get_available_levels()
    MAX_LEVEL = max(available) if available else level_number

    if clear_groups:
        world_data = reset_level()
    else:
        world_data = []
        for row in range(ROWS):
            r = [-1] * COLUMNS
            world_data.append(r)

    overrides = load_level_overrides()
    if str(LEVEL) in overrides:
        for x, row in enumerate(overrides[str(LEVEL)]):
            if x >= ROWS:
                break
            for y, tile in enumerate(row[:COLUMNS]):
                world_data[x][y] = int(tile)
    else:
        with open(level_file_path(LEVEL), newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                if x >= ROWS:
                    break
                for y, tile in enumerate(row[:COLUMNS]):
                    world_data[x][y] = int(tile)

    world = World()
    player, health_bar = world.process_data(world_data)

def make_menu_buttons():
    buttons = []
    levels = get_available_levels()
    button_width = 74
    button_height = 26
    start_x = 45
    start_y = MENU_LEVEL_TOP
    gap_x = 10
    gap_y = 12
    for index, level_number in enumerate(levels):
        x = start_x + (index % 5) * (button_width + gap_x)
        y = start_y + (index // 5) * (button_height + gap_y)
        if MENU_LEVEL_TOP <= y and y + button_height <= MENU_LEVEL_BOTTOM:
            buttons.append((level_number, TextButton(x, y, button_width, button_height, f"Level {level_number}")))
    return buttons

def get_menu_scroll_max():
    return 0

def launch_level_editor():
    if getattr(sys, "frozen", False):
        subprocess.Popen([sys.executable, "--editor"], cwd=APP_DIR)
        return
    subprocess.Popen([sys.executable, os.path.join(APP_DIR, "level_editor.py")], cwd=APP_DIR)

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction ==1 : #whole screen screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2 , SCREEN_HEIGHT))
            pygame.draw.rect(screen,self.colour, (SCREEN_WIDTH //2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen,self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT //2))
            pygame.draw.rect(screen,self.colour, (0, SCREEN_HEIGHT // 2+ self.fade_counter , SCREEN_WIDTH, SCREEN_HEIGHT))
       
        if self.direction ==2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete
    

# cretae screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade= ScreenFade(2, PINK, 4)

# create btns 
start_button = Button(SCREEN_WIDTH // 2 -130, SCREEN_HEIGHT //2 -150, start_img, 1)
exit_button = Button(SCREEN_WIDTH // 2 -110, SCREEN_HEIGHT //2 + 50, exit_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 -100, SCREEN_HEIGHT //2 - 50, restart_img, 2)
restart_button.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
death_menu_button = TextButton(SCREEN_WIDTH // 2 - 55, SCREEN_HEIGHT // 2 + 70, 110, 32, "Menu", (69, 123, 157))
game_menu_button = TextButton(SCREEN_WIDTH - 76, 10, 66, 28, "Menu", (69, 123, 157))
menu_play_button = TextButton(SCREEN_WIDTH // 2 - 65, 58, 130, 32, "Play", (65, 145, 92))
MENU_LEVEL_TOP = 122
MENU_LEVEL_BOTTOM = 190
menu_scroll = 0
make_level_button = TextButton(SCREEN_WIDTH // 2 - 76, 244, 152, 32, "Edit Levels", (65, 145, 92))
menu_exit_button = TextButton(SCREEN_WIDTH // 2 - 48, 294, 96, 30, "Exit", (180, 68, 58))


# # temp - create item boxes
# item_box = ItemBox("Health",100, 260)
# item_box_group.add(item_box)
# item_box = ItemBox("Ammo",400, 260)
# item_box_group.add(item_box)
# item_box = ItemBox("Grenade",500, 260)
# item_box_group.add(item_box)

#--create the instance-- # x,y:coordinates i want to draw the players
## AS THIS CANBE MADE IN LEVEL MAKING  -- WE HAVE THE PLAYER & ENEMY MAKING IN THERE
# player= Soldier("player",200,200,1.3,5, 20,5)      # x,y=200 & scale=2 speed=5--how many pixels it gonna move
# health_bar = HealthBar(10 , 10, player.health, player.health)

# enemy= Soldier("enemy",500,200,1.3,2, 20,0)
# enemy2= Soldier("enemy",300,300,1.3,2, 20,0)
# enemy_group.add(enemy) # add the enemy to the enemy group so that we can draw it on the screen and update its position later on in the game
# enemy_group.add(enemy2)

world_data = []
world = None
player = None
health_bar = None
menu_level_buttons = make_menu_buttons()
if menu_level_buttons:
    load_level(menu_level_buttons[0][0], clear_groups=False)



# if u run this teh screen popsup for a split sec and closes : reason:code runs toptobottom and nothign to continue doign it 
# to avoid this we need to create a game loop
# game loop that continues until the game is quitconi
run= True  #so while the run is T the game would run
while run:
    
    clock.tick(FPS)

    if start_game == False:
        # draw main menu
        draw_bg()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (9, 18, 24, 80), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(overlay, (0, 0))

        title_img = font.render("SHOOTER", True, WHITE)
        screen.blit(title_img, title_img.get_rect(center=(SCREEN_WIDTH // 2, 28)))

        if menu_play_button.draw(screen) and player is not None:
            load_level(LEVEL)
            bg_scroll = 0
            screen_scroll = 0
            start_game = True
            start_intro = True
            start_button.clicked = False

        panel_rect = pygame.Rect(28, MENU_LEVEL_TOP - 16, 444, MENU_LEVEL_BOTTOM - MENU_LEVEL_TOP + 32)
        pygame.draw.rect(screen, (13, 22, 27, 210), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255, 70), panel_rect, 1, border_radius=8)

        menu_level_buttons = make_menu_buttons()
        for level_number, level_button in menu_level_buttons:
            if level_button.draw(screen):
                load_level(level_number)
                bg_scroll = 0
                screen_scroll = 0
                start_game = True
                start_intro = True

        if make_level_button.draw(screen):
            launch_level_editor()

        if menu_exit_button.draw(screen):
            run = False
    else:
        # draw world map
        draw_bg()
        world.draw() # this would call the draw method of the world class and draw the world on the screen
        # draw_text("Level: " + str(LEVEL), font, WHITE, TILE_SIZE, 10) # this would draw the level number on the screen at the top left corner and we are converting the level number to a string so that we can concatenate it with the "Level: " string and display it on the screen

        # show Health bar
        health_bar.draw(player.health)
        # show ammo
        draw_icon_counter(bullet_img, player.ammo, 10, 44)
        # show grenades
        draw_icon_counter(grenade_img, player.grenades, 88, 44)
        if game_menu_button.draw(screen):
            start_game = False
            start_intro = False
            bg_scroll = 0
            screen_scroll = 0
            moving_left = False
            moving_right = False
            shoot = False
            grenade = False
            grenade_thrown = False
        
        player.update()
        player.draw() # this would call the draw method of the player class and draw the player on the screen
        
        for enemy in enemy_group:
            enemy.update()   
            enemy.ai() # ai method is avaliable for all char
            enemy.draw()  

        decoration_group.update()
        water_group.update()
        exit_group.update()
        item_box_group.update()
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        item_box_group.draw(screen)
        # update bullets / grenades / explosions and draw them
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)

        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0: # if the grenade button is pressed and the grenade has not been thrown yet and the player has grenades left then we can throw a grenade
                grenade = Grenade(player.rect.centerx + (0.5*player.rect.size[0]* player.direction),
                                player.rect.top, player.direction)
                grenade_group.add(grenade)
                # grenades reduce 
                player.grenades -= 1
                grenade_thrown = True
                
            if player.in_air:
                player.update_action(2) # jump action
            elif moving_left or moving_right:
                player.update_action(1) # 1 : run action
            else:
                player.update_action(0) # 0 : idle action
            screen_scroll, level_complete = player.move(moving_left, moving_right)  # moving the players now # the player isrunning to fast cuz no framae limit
            bg_scroll -= screen_scroll
            # check if level completed
            if level_complete:
                start_intro = True
                next_level = LEVEL + 1
                bg_scroll = 0
                if next_level in get_available_levels():
                    load_level(next_level)
                else:
                    start_game = False


        else:
            screen_scroll = 0
             # screen fading
            if player.vanished and death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0 
                    start_intro = True
                    bg_scroll = 0  
                    load_level(LEVEL)
                if death_menu_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_game = False
                    start_intro = False
                    bg_scroll = 0
                    screen_scroll = 0

    
    for event in pygame.event.get(): # this would give all enets : press the button, mouse, or any key and it woudl get registerd by this var here
        if event.type== pygame.QUIT:
            run=False

        # keyboard presses
        if event.type==pygame.KEYDOWN: # any key pressed on keyboard
            if event.key== pygame.K_LEFT: # if the left arrow key is pressed
                moving_left=True
            if event.key== pygame.K_RIGHT: # if the right arrow key is pressed
                moving_right=True
            if event.key== pygame.K_SPACE: # if the key pressed is SPACE
                shoot = True
            if event.key== pygame.K_q: # if the key pressed is q
                grenade = True
            if (event.key== pygame.K_w or event.key == pygame.K_UP) and player is not None and player.alive: # W or up arrow jumps
                player.jump=True
                jump_fx.play()
            if event.key== pygame.K_ESCAPE: # if the key pressed is ESC to quit game
                run=False

        # keyboard button released
        if event.type==pygame.KEYUP: # any key pressed on keyboard
            if event.key== pygame.K_LEFT: # if the left arrow key is released
                moving_left=False
            if event.key== pygame.K_RIGHT: # if the right arrow key is released
                moving_right=False
            if event.key== pygame.K_SPACE: # if the key pressed is SPACE
                shoot = False
            if event.key== pygame.K_q: # if the key pressed is q
                grenade = False
                grenade_thrown = False


    pygame.display.update()  # this would update the display with the new changes we made to the screen (like drawing the img)
pygame.quit() # you click thecross button and this event is called which then sets run to false and the game loop ends and then this line is executed which quits the game


  # direction variable: this variable would be used to determine the direction of the player, if the player is moving left then the direction would be -1 and if the player is moving right then the direction would be 1, this variable would be used to flip the img when moving left and also to determine the direction of the bullets when we shoot them later on in the game
  #transfrom : this is used to change the size of the img or flip it or rotate it, we can use it to make the img bigger or smaller or flip it horizontally or vertically or rotate it by a certain angle, for example if we want to make the img 2 times bigger we can do pygame.transform.scale(img,(img.get_width()*2 ,img.get_height()*2)) and if we want to flip the img horizontally we can do pygame.transform.flip(img, True, False) and if we want to rotate the img by 90 degrees we can do pygame.transform.rotate(img, 90)
 
