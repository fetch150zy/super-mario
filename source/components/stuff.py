# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:32
@Auth ： Mars
@File ：stuff.py
@IDE ：PyCharm
"""
# 这个文件主要用于存放一些杂项部分
import pygame as pg
from .. import const_var as cst, tools, setup


class Item(pg.sprite.Sprite):
    '''
    游戏中的地面，水管，台阶等
    '''
    def __init__(self, x, y, w, h, name):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w, h)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name


class Checkpoint(Item):
    '''
    检查点（用于激活敌人）
    '''
    def __init__(self, x, y, w, h, checkpoint_type, enemy_groupid=None, name='checkpoint'):
        Item.__init__(self, x, y, w, h, name)
        self.checkpoint_type = checkpoint_type
        self.enemy_groupid = enemy_groupid


class Stuff(pg.sprite.Sprite):
    '''
    杂项的基类
    '''
    def __init__(self, x, y, sheet, frame_rects, scale):
        pg.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        for frame_rect in frame_rects:
            self.frames.append(tools.get_img(sheet, *frame_rect, cst.BLACK, scale))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        pass


class CastleFlag(Stuff):
    '''
    城堡通关的旗帜
    '''
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS[cst.ITEM_OBJECTS],
                       [(129, 2, 14, 14)], cst.FLAG_MULTI)
        self.y_vel = -2
        self.final_height = y

    def update(self):
        '''
        通关时城堡升起旗帜
        :return: 无
        '''
        if self.rect.bottom > self.final_height:
            self.rect.y += self.y_vel


class Flag(Stuff):
    '''
    旗帜
    '''
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS[cst.ITEM_OBJECTS],
                [(128, 32, 16, 16)], cst.FLAG_MULTI)
        self.state = 'top'
        self.y_vel = 5

    def update(self):
        '''
        旗帜下滑
        :return: 无
        '''
        if self.state == cst.FLAGPOLE_SLIDE_STATE:
            self.rect.y += self.y_vel
            if self.rect.bottom >= 485:
                self.state = cst.FLAGPOLE_BOTTOM_STATE


class Pole(Stuff):
    '''
    旗杆
    '''
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS[cst.TILE_SET],
                [(263, 144, 2, 16)], cst.BRICK_MULTI)


class PoleTop(Stuff):
    '''
    旗杆顶部
    '''
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS[cst.TILE_SET],
                [(228, 120, 8, 8)], cst.BRICK_MULTI)


class Digit(pg.sprite.Sprite):
    '''
    主要就是给数字赋予一些精灵属性
    '''
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()


class Score:
    '''
    得分类（主要实现得分时分数蹦出的效果）
    '''
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.y_vel = -3
        self.create_images_dict()
        self.score = score
        self.create_score_digit()
        self.distance = 130 if self.score == 1000 else 75

    def create_images_dict(self):
        '''
        抠图
        :return: 无
        '''
        self.image_dict = {}
        digit_rects = [(1, 168, 3, 8), (5, 168, 3, 8),
                           (8, 168, 4, 8), (0, 0, 0, 0),
                           (12, 168, 4, 8), (16, 168, 5, 8),
                           (0, 0, 0, 0), (0, 0, 0, 0),
                           (20, 168, 4, 8), (0, 0, 0, 0)]
        digit_string = '0123456789'
        for digit, image_rect in zip(digit_string, digit_rects):
            self.image_dict[digit] = tools.get_img(setup.GRAPHICS[cst.ITEM_OBJECTS],
                                                     *image_rect, cst.BLACK, cst.BRICK_MULTI)

    def create_score_digit(self):
        '''
        创建数字图层
        :return: 无
        '''
        self.digit_group = pg.sprite.Group()
        self.digit_list = []
        for digit in str(self.score):
            self.digit_list.append(Digit(self.image_dict[digit]))

        for i, digit in enumerate(self.digit_list):
            digit.rect = digit.image.get_rect()
            digit.rect.x = self.x + (i * 10)
            digit.rect.y = self.y

    def update(self, score_list):
        '''
        更新数字状态（数字有一个上升的过程，达到一定高度后消失）
        :param score_list: 得分表（里面都是精灵组）
        :return: 无
        '''
        for digit in self.digit_list:
            digit.rect.y += self.y_vel

        if (self.y - self.digit_list[0].rect.y) > self.distance:
            score_list.remove(self)

    def draw(self, screen):
        '''
        在图层上绘制
        :param screen: 图层
        :return: 无
        '''
        for digit in self.digit_list:
            screen.blit(digit.image, digit.rect)
