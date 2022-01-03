# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:33
@Auth ： Mars
@File ：const_var.py
@IDE ：PyCharm
"""
'''
    这个文件定义一些游戏中的常量
'''

# 屏幕尺寸相关
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# 图片缩放相关
BG_MULTI = 2.68
PLAYER_MULTI = 2.8
BRICK_MULTI = 2.69
ENEMY_MULTI = 2.5
FLAG_MULTI = 2.5

# 字体缩放
WIDTH_SCALE = 1.25
HEIGHT_SCALE = 1.15

# 敌人运动速度
ENEMY_SPEED = 1

# 字体
FONT = 'FixedSys.ttf'
FONT_SIZE = 40

# 全局重力
GRAVITY = 1.0
ANTI_GRAVITY = 0.3

# 地面高度
GROUND_HEIGHT = SCREEN_HEIGHT - 62

# 标题
ORIGINAL_CAPTION = '超级玛丽'

# 游戏状态信息
STATE_MAIN_MENU = 'main_menu'
STATE_LOAD_SCREEN = 'load_screen'
STATE_LEVEL = 'level'
STATE_GAME_OVER = 'game_over'
STATE_TIME_OUT = 'time_out'
STATE_YOU_DIE = 'you_die'
STATE_YOU_WIN = 'you_win'
START_STATE = 'main_menu'

# 文本信息
CHOICE_GAME_EASY = '1 EASY GAME'
CHOICE_GAME_HARD = '2 HARD GAME'
RANK_LABEL = 'RANK - '
RANK_INFO = '114514'
WORLD_LABEL = 'WORLD'
LIVES_LABEL = 'x    {}'
JOKE_INFO_1 = 'Help!!! Mars_wz was captured by the dragon.'
JOKE_INFO_2 = 'If it\'s a brother, come and save me..'
GAME_OVER_LABEL = 'GAME OVER'
YOU_DIE_LABEL = 'YOU DIE'
SCORE_LABEL = 'SCORE'
TIME_LABEL = 'TIME'
TIME_OUT_LABEL = 'TIME OUT'
YOU_WIN_LABEL = 'YOU WIN'

# 颜色
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CYAN = (0, 100, 100)

# 素材包
ENEMIES = 'enemies'
ITEM_OBJECTS = 'item_objects'
LEVEL_1 = 'level_1'
MARIO_BROS = 'mario_bros'
SMB_ENEMIES_SHEET = 'smb_enemies_sheet'
TEXT_IMAGES = 'text_images'
TILE_SET = 'tile_set'
TITLE_SCREEN = 'title_screen'

# 素材包格式
RESOURCE_FORMAT = ('.jpg', '.png', '.bmp', '.gif')

# 状态持续时间
GAME_OVER_DURATION = 4000
LOAD_SCREEN_DURATION = 2000
DEAD_DURATION = 3000
TIME_OUT_DURATION = 220000

# game info
GAIN_SCORES = 'score'
GAIN_COINS = 'coin'
PLAYER_LIVES = 'lives'
PLAYER_STATE = 'player_state'
EASY_OR_HARD = 'easy_or_hard'
REMAINING_TIME = 'remaining_time'

EASY_GAME_LIVES = 3
HARD_GAME_LIVES = 2
MARIO_START_STATE = 'small'
EASY_GAME = 'easy'
HARD_GAME = 'hard'

# 路径相关
MAP_PATH = 'source/data/maps'
PLAYER_PATH = 'source/data/player'

# 马里奥状态信息
PLAYER_STAND_STATE = 'stand'
PLAYER_WALK_STATE = 'walk'
PLAYER_JUMP_STATE = 'jump'
PLAYER_FALL_STATE = 'fall'
PLAYER_DIE_STATE = 'die'
PLAYER_SMALL_TO_BIG = 'small2big'
PLAYER_BIG_TO_SMALL = 'big2small'
PLAYER_BIG_TO_FIRE = 'big2fire'
PLAYER_RAP = 'rap'
PLAYER_BASKETBALL = 'basketball'

# 砖块状态
BRICK_REST_STATE = 'rest'
BRICK_BUMPED_STATE = 'bumped'
BRICK_OPEN_STATE = 'open'

# 宝箱状态
BOX_REST_STATE = 'rest'
BOX_BUMPED_STATE = 'bumped'
BOX_OPEN_STATE = 'open'

# 敌人状态
ENEMY_WALK_STATE = 'walk'
ENEMY_FALL_STATE = 'fall'
ENEMY_DIE_STATE = 'die'
ENEMY_TRAMPLED_STATE = 'trampled'
ENEMY_BUMPED_STATE = 'bumped'
ENEMY_SLIDE_STATE = 'slide'

# 道具状态
PROP_REST_STATE = 'rest'
PROP_WALK_STATE = 'walk'
PROP_GROW_STATE = 'grow'
PROP_FALL_STATE = 'fall'

FIREBALL_FLY_STATE = 'fly'
FIREBALL_BOOM_STATE = 'boom'

# 旗帜相关
FLAGPOLE_TOP_STATE = 'top'
FLAGPOLE_SLIDE_STATE = 'slide_down'
FLAGPOLE_BOTTOM_STATE = 'bottom'

FLAGPOLE = 'flagpole'
FLAGPOLE_FLAG = 0
FLAGPOLE_POLE = 1
