# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:26
@Auth ： Mars
@File ：box.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import tools, setup
from .. import const_var as cst
from .powerup import create_powerup


class Box(pg.sprite.Sprite):
    '''
    宝箱类
    '''
    def __init__(self, x, y, box_type, group, game_info, level, name='box'):
        pg.sprite.Sprite.__init__(self)
        self.level = level
        self.game_info = game_info
        self.x = x
        self.y = y
        self.box_type = box_type
        self.group = group
        self.name = name
        self.frame_rects = [
            (384, 0, 16, 16),
            (400, 0, 16, 16),
            (416, 0, 16, 16),
            (432, 0, 16, 16)
        ]

        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_img(setup.GRAPHICS[cst.TILE_SET], *frame_rect,
                                             (0, 0, 0), cst.BRICK_MULTI))
            self.frame_index = 0
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.x = self.x
            self.rect.y = self.y

            self.state = cst.BOX_REST_STATE
            self.timer = 0
            self.gravity = cst.GRAVITY

    def update(self):
        '''
        必备的update
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        self.handle_states()

    def handle_states(self):
        '''
        宝箱状态总控
        :return: 无
        '''
        if self.state == cst.BOX_REST_STATE:
            self.rest()
        elif self.state == cst.BOX_BUMPED_STATE:
            self.bumped()
        elif self.state == cst.BOX_OPEN_STATE:
            self.open()

    def rest(self):
        '''
        初始时比砖块复杂一些，有一个闪烁的功能
        :return: 无
        '''
        frame_durations = [400, 100, 100, 50]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index = (self.frame_index + 1) % 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def go_bumped(self):
        '''
        被顶了小跳一下
        :return: 无
        '''
        self.y_vel = -5
        self.state = cst.BOX_BUMPED_STATE

    def bumped(self):
        '''
        宝箱被顶，实现和砖块差不多
        :return: 无
        '''
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        self.frame_index = 3
        self.image = self.frames[self.frame_index]

        if self.rect.y > self.y + 10:
            self.rect.y = self.y
            self.state = cst.BOX_OPEN_STATE

            if self.box_type == 1:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type))
                self.level.update_score(200, self, coin_num=1)
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type))

    def open(self):
        pass