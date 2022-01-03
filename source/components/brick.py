# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:27
@Auth ： Mars
@File ：brick.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import const_var as cst
from .. import  tools, setup
from .powerup import create_powerup
from . import stuff


class Brick(pg.sprite.Sprite):
    '''
    砖块类
    '''
    def __init__(self, x, y, brick_type, group, game_info, level, color=None, name='brick'):
        pg.sprite.Sprite.__init__(self)
        self.level = level
        self.game_info = game_info
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.group = group
        self.name = name
        bright_rect_frames = [(16, 0, 16, 16), (48, 0, 16, 16)]
        dark_rect_frames = [(16, 32, 16, 16), (48, 32, 16, 16)]

        # 载入了两种贴图（分别是地上和地下的）
        if not color:
            self.frame_rects = bright_rect_frames
        else:
            self.frame_rects = dark_rect_frames

        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_img(setup.GRAPHICS[cst.TILE_SET], *frame_rect,
                                             (0, 0, 0), cst.BRICK_MULTI))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.state = cst.BRICK_REST_STATE
        self.gravity = cst.GRAVITY

    def update(self):
        '''
        必备update方法
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        self.handle_states()

    def handle_states(self):
        '''
        砖块状态主控
        :return: 无
        '''
        if self.state == cst.BRICK_REST_STATE:
            self.rest()
        elif self.state == cst.BRICK_BUMPED_STATE:
            self.bumped()
        elif self.state == cst.BRICK_OPEN_STATE:
            self.open()

    def rest(self):
        '''
        初始状态啥也不用干
        :return: 无
        '''
        pass

    def go_bumped(self):
        '''
        被顶了小跳一下
        :return: 无
        '''
        self.y_vel = -5
        self.state = cst.BRICK_BUMPED_STATE

    def bumped(self):
        '''
        被顶后回到初始位置并做相应处理
        :return: 无
        '''
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y > self.y + 5:
            self.rect.y = self.y
            self.state = cst.BRICK_OPEN_STATE

            if self.brick_type == 0:
                self.state = cst.BRICK_REST_STATE
            elif self.brick_type == 1:
                    self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.brick_type))
                    self.level.update_score(200, self, coin_num=1)
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.brick_type))

    def open(self):
        '''
        砖块被顶后处于打开状态
        :return: 无
        '''
        self.frame_index = 1
        self.image = self.frames[self.frame_index]

    def smashed(self, group):
        '''
        砖块被变大的马里奥顶碎
        :param group: 死亡组的砖块
        :return: 无
        '''
        debris = [          # 爆炸后的残骸（x, y, x_v, y_v)
            (self.rect.x, self.rect.y, -2, -10),
            (self.rect.x, self.rect.y, 2, -10),
            (self.rect.x, self.rect.y, -2, -5),
            (self.rect.x, self.rect.y, 2, -5),
        ]
        for db in debris:
            group.add(Debris(*db))
        self.kill()


class Debris(pg.sprite.Sprite):
    '''
    对残骸的运动状态进行处理
    '''
    def __init__(self, x, y, x_vel, y_vel):
        pg.sprite.Sprite.__init__(self)
        self.image = tools.get_img(setup.GRAPHICS[cst.TILE_SET], 68, 20, 8, 8, (0, 0, 0), cst.BRICK_MULTI)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.gravity = cst.GRAVITY

    def update(self, *args):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > cst.SCREEN_HEIGHT:
            self.kill()
