# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:27
@Auth ： Mars
@File ：coin.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import const_var as cst
from .. import tools, setup


class FlashCoin(pg.sprite.Sprite):
    '''
    游戏界面中的金币（闪烁的那个，不是游戏中的金币）
    '''
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.frames = []    # 存储金币贴图
        self.frame_index = 0    # 帧索引
        frame_rects = [(1, 160, 5, 8), (9, 160, 5, 8), (17, 160, 5, 8), (9, 160, 5, 8)]
        self.load_frames(frame_rects)   # 将载入的金币贴图存储到frame中
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = 280
        self.rect.y = 58
        self.timer = 0    # 计时器

    def load_frames(self, frame_rects):
        '''
        载入金币贴图
        :param frame_rects: 帧
        :return: 无
        '''
        sheet = setup.GRAPHICS[cst.ITEM_OBJECTS]
        for frame_rect in frame_rects:
            self.frames.append(tools.get_img(sheet, *frame_rect, (0, 0, 0), cst.BG_MULTI))

    def update(self):
        '''
        实现闪烁功能
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        frame_durations = [375, 125, 125, 125]    # 帧持续时间（375， 125， 125， 125）毫秒

        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time

        self.image = self.frames[self.frame_index]


class Coin(pg.sprite.Sprite):
    '''
    游戏中出现的金币
    '''
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        self.frame_rects = [(52, 113, 8, 14), (4, 113, 8, 14), (20, 113, 8, 14), (36, 113, 8, 14)]
        self.load_frames(self.frame_rects)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y - 5
        self.gravity = cst.GRAVITY
        self.y_vel = -15
        self.timer = 0
        self.initial_height = self.rect.bottom - 5

    def load_frames(self, frame_rects):
        '''
        载入金币贴图
        :param frame_rects: 像素矩阵坐标
        :return: 无
        '''
        for frame_rect in frame_rects:
            self.frames.append(tools.get_img(setup.GRAPHICS[cst.ITEM_OBJECTS],
                                             *frame_rect, (0, 0, 0), cst.BG_MULTI))

    def update(self, game_info):
        '''
        统一格式
        :param game_info: 通用游戏数据
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        self.spin_coin()

    def spin_coin(self):
        '''
        金币螺旋上升
        :return: 无
        '''
        self.image = self.frames[self.frame_index]
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if (self.current_time - self.timer) > 80:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.timer = self.current_time

        if self.rect.bottom > self.initial_height:
            self.kill()
