# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:28
@Auth ： Mars
@File ：powerup.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import setup, tools
from .. import const_var as cst
from .. components import coin

def create_powerup(centerx, centery, type):
    '''
    创建强化道具
    :param centerx: x
    :param centery: y
    :param type: 道具种类
    :return: 创建的道具实例
    '''
    if type == 1:        # 蹦金币
        return coin.Coin(centerx, centery)
    elif type == 3:      # 长蘑菇
        return Mushroom(centerx, centery)
    elif type == 4:      # 长花
        return Fireflower(centerx, centery)


class Powerup(pg.sprite.Sprite):
    '''
    所有强化道具的基类
    '''
    def __init__(self, centerx, centery, frame_rects):
        pg.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        for frame_rect in frame_rects:
            self.frames.append(tools.get_img(setup.GRAPHICS[cst.ITEM_OBJECTS],
                                             *frame_rect, (0, 0, 0), 2.5))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.origin_y = centery - self.rect.height / 2

        self.x_vel = 0
        self.direction = 1
        self.y_vel = -1
        self.gravity = 1
        self.max_y_vel = 8


    def update_pos(self, level):
        '''
        移动道具的位置检测（主要被子类的update方法调用）
        :param level: level类（主要用于碰撞检测）
        :return: 无
        '''
        self.rect.x += self.x_vel
        self.check_x_collisions(level)  # x方向碰撞检测
        self.rect.y += self.y_vel
        self.check_y_collisions(level)  # y方向碰撞检测

        if self.rect.x < 0 or self.rect.y > cst.SCREEN_HEIGHT:
            self.kill()        # 离开地图范围就销毁

    def check_x_collisions(self, level):
        '''
        x方向检测（和player一致），主要用于可移动道具与其它组件的检测
        :param level: level类（主要用到level类中的地面，水管，台阶精灵组）
        :return: 无
        '''
        sprite = pg.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            if self.direction:
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1

    def check_y_collisions(self, level):
        '''
        y方向检测（和player一致），主要用于可移动道具与其它组件的检测
        :param level: level类（主要用到level类中的地面，水管，台阶，宝箱，砖块等精灵组；还有level类中实现的下落检测）
        :return: 无
        '''
        check_ground = pg.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pg.sprite.spritecollideany(self, check_ground)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = cst.PROP_WALK_STATE

        level.check_will_fall(self)


class Mushroom(Powerup):
    '''
    变大蘑菇（主要有三个动作：生长，移动，下落）
    '''
    def __init__(self, centerx, centery):
        Powerup.__init__(self, centerx, centery, [(0, 0, 16, 16)])
        self.x_vel = 2
        self.state = cst.PROP_GROW_STATE
        self.name = 'mushroom'

    def update(self, level):
        '''
        更新蘑菇的动作状态，因为蘑菇类的基类没有update方法，这个方法主要就是调用基类中的update_pos方法实现碰撞检测
        还实现了蘑菇的生长和状态切换
        :param level: level类
        :return: 无
        '''
        if self.state == cst.PROP_GROW_STATE:
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = cst.PROP_WALK_STATE
        elif self.state == cst.PROP_WALK_STATE:
            pass
        elif self.state == cst.PROP_FALL_STATE:
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity

        if self.state != cst.PROP_GROW_STATE:
            self.update_pos(level)


class Fireflower(Powerup):
    '''
    火焰花（主要有两个状态：生长，静止）
    '''
    def __init__(self, centerx, centery):
        frame_rects = [(0, 32, 16, 16), (16, 32, 16, 16), (32, 32, 16, 16), (48, 32, 16, 16)]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.state = cst.PROP_GROW_STATE
        self.name = 'fireflower'
        self.timer = 0

    def update(self, level):
        '''
        与蘑菇类的update方法略有不同，主要是实现火焰花静止时的帧切换和生长状态以及状态的切换
        :param level: level类（此处用不到，因为update方法是统一调度，此处写法固定）
        :return: 无
        '''
        if self.state == cst.PROP_GROW_STATE:
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = cst.PROP_REST_STATE

        self.current_time = pg.time.get_ticks()

        if self.timer == 0:
            self.timer = self.current_time
        if self.current_time - self.timer > 30:
            self.frame_index += 1
            self.frame_index %= len(self.frames)
            self.timer = self.current_time
            self.image = self.frames[self.frame_index]


class Fireball(Powerup):
    '''
    强化道具发射火球（主要有两个状态：飞行，爆炸）
    '''
    def __init__(self, centerx, centery, direction):
        frame_rects = [
            (96, 144, 8, 8), (104, 144, 8, 8), (96, 152, 8, 8), (104, 152, 8, 8),    # 旋转
            (112, 144, 16, 16), (112, 160, 16, 16), (112, 176, 16, 16),              # 爆炸
        ]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.name = 'fireball'
        self.state = cst.FIREBALL_FLY_STATE
        self.direction = direction
        self.x_vel = 10 if self.direction else -10
        self.y_vel = 10
        self.gravity = 1
        self.timer = 0

    def update(self, level):
        '''
        实现飞行状态的帧切换和碰撞检测，调用的update_pos方法为重写的基类方法
        :param level: level类，用于碰撞检测（包括障碍物和敌人等）
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        if self.state == cst.FIREBALL_FLY_STATE:    # 火焰弹发射后为飞行状态
            self.y_vel += self.gravity
            if self.current_time - self.timer > 200:
                self.frame_index += 1
                self.frame_index %= 4
                self.timer = self.current_time
                self.image = self.frames[self.frame_index]
            self.update_pos(level)
        elif self.state == cst.FIREBALL_BOOM_STATE:   # 碰到敌人或障碍物会爆炸
            if self.current_time - self.timer > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                    self.timer = self.current_time
                    self.image = self.frames[self.frame_index]
                else:
                    self.kill()

    def update_pos(self, level):
        '''
        调用子类重写的x,y碰撞检测
        :param level: level类（用来碰撞检测）
        :return: 无
        '''
        self.rect.x += self.x_vel
        self.check_x_collisions(level)  # x方向碰撞检测
        self.rect.y += self.y_vel
        self.check_y_collisions(level)  # y方向碰撞检测

        if self.rect.x < 0 or self.rect.y > cst.SCREEN_HEIGHT:
            self.kill()

    def check_x_collisions(self, level):
        '''
        火焰弹与水平障碍物和敌人的碰撞检测
        :param level: level类（用到了level中的障碍物组和敌人组）
        :return: 无
        '''
        sprite = pg.sprite.spritecollideany(self, level.ground_items_group)   # 与水平方向障碍物的碰撞检测
        if sprite:
            self.frame_index = 4
            self.state = cst.FIREBALL_BOOM_STATE

        kill_enemy = pg.sprite.spritecollideany(self, level.enemy_group)      # 与敌人的检测
        if kill_enemy:
            self.state = cst.FIREBALL_BOOM_STATE
            if kill_enemy.name == 'goomba':
                kill_enemy.kill()
                level.update_score(100, self, coin_num=0)
            if kill_enemy.name == 'koopa':
                kill_enemy.state = cst.ENEMY_TRAMPLED_STATE


    def check_y_collisions(self, level):
        '''
        与竖直方向碰撞检测，与水平方向不同，我们不更新状态，只进行反弹
        :param level: level类（用到了level中的障碍物组，宝箱组，砖块组）
        :return: 无
        '''
        check_ground = pg.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pg.sprite.spritecollideany(self, check_ground)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = -10


class LifeMushroom(Powerup):
    '''
    加生命蘑菇
    '''
    pass


class Star(Powerup):
    '''
    无敌星星
    '''
    pass