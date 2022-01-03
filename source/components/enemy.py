# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:28
@Auth ： Mars
@File ：enemy.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import setup, tools
from .. import const_var as cst


def create_enemy(enemy_data):
    '''
    创建敌人
    :param enemy_data: 敌人列表
    :return: 无
    '''
    enemy_type = enemy_data['type']
    x, y_bottom, direction, color = enemy_data['x'], enemy_data['y'], enemy_data['direction'], enemy_data['color']

    if enemy_type == 0:    # 蘑菇怪
        enemy = Goomba(x, y_bottom, direction, 'goomba', color)
    elif enemy_type == 1:    # 乌龟怪
        enemy = Koopa(x, y_bottom, direction, 'koopa', color)
    return enemy


class Enemy(pg.sprite.Sprite):
    '''
    敌人类
    '''
    def __init__(self, x, y_bottom, direction, name, frame_rects):
        pg.sprite.Sprite.__init__(self)
        self.direction = direction
        self.timer = 0
        self.name = name
        self.frame_index = 0
        self.left_frames = []
        self.right_frames = []

        self.load_frames(frame_rects)
        self.frames = self.left_frames if self.direction == 0 else self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y_bottom

        self.x_vel = -1 * cst.ENEMY_SPEED if self.direction == 0 else cst.ENEMY_SPEED
        self.y_vel = 0
        self.gravity = cst.GRAVITY
        self.rect.bottom = y_bottom
        self.state = cst.ENEMY_WALK_STATE

    def load_frames(self, frame_rects):
        '''
        载入敌人贴图
        :param frame_rects: 帧
        :return: 无
        '''
        for frame_rect in frame_rects:
            left_frame = tools.get_img(setup.GRAPHICS['enemies'], *frame_rect,
                                       (0, 0, 0), cst.ENEMY_MULTI)
            right_frame = pg.transform.flip(left_frame, True, False)
            self.left_frames.append(left_frame)
            self.right_frames.append(right_frame)

    def update(self, level):
        '''
        敌人大部分操作和玩家是一致的，直接copy
        :param level: 关卡
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        self.handle_states(level)
        self.update_pos(level)

    def handle_states(self, level):
        '''
        敌人状态总控
        :param level: level类，用于碰撞检测
        :return: 无
        '''
        if self.state == cst.ENEMY_WALK_STATE:    # 移动
            self.walk()
        elif self.state == cst.ENEMY_FALL_STATE:    # 下落
            self.fall()
        elif self.state == cst.ENEMY_DIE_STATE:    # 死亡
            self.die()
        elif self.state == cst.ENEMY_TRAMPLED_STATE:    # 被踩
            self.trampled(level)
        elif self.state == cst.ENEMY_SLIDE_STATE:     # 溜溜球
            self.slide(level)

        if self.direction:    # 和玩家一样，根据敌人速度矢量朝向镜像翻转贴图
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def walk(self):
        '''
        敌人的移动方法，和玩家移动操作一致
        :return: 无
        '''
        if self.current_time - self.timer > 125:
            self.frame_index = (self.frame_index + 1) % 2
            self.image = self.frames[self.frame_index]
            self.timer = self.current_time

    def fall(self):
        '''
        敌人下落方法
        :return: 无
        '''
        if self.y_vel < 10:    # 速度小于10就一直按照预定重力加速度下落
            self.y_vel += self.gravity

    def die(self):
        '''
        敌人死亡方法
        :return:
        '''
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > cst.SCREEN_HEIGHT:
            self.kill()

    def trampled(self, level):
        '''
        被踩扁（留给子类重写）
        :param level:
        :return:
        '''
        pass

    def slide(self, level):
        '''
        溜溜球功能（也留给子类重写）
        :param level:
        :return:
        '''
        pass

    def update_pos(self, level):
        '''
        更新敌人位置（主要调用x，y方向的检测函数）
        :param level: level类，用于碰撞检测
        :return: 无
        '''
        self.rect.x += self.x_vel
        self.check_x_collisions(level)       # x方向碰撞检测
        self.rect.y += self.y_vel
        if self.state != cst.ENEMY_DIE_STATE:
            self.check_y_collisions(level)       # y方向碰撞检测

    def check_x_collisions(self, level):
        '''
        x方向碰撞检测
        :param level: level类，用于碰撞检测
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

        if self.state == cst.ENEMY_SLIDE_STATE:
            enemy = pg.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                enemy.go_die(how_to_die=cst.ENEMY_SLIDE_STATE, direction=self.direction)
                level.enemy_group.remove(enemy)
                level.dead_group.add(enemy)
                level.update_score(100, enemy, coin_num=0)

    def check_y_collisions(self, level):
        '''
        y方向碰撞检测
        :param level: level类，用于碰撞检测
        :return: 无
        '''
        check_ground = pg.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pg.sprite.spritecollideany(self, check_ground)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = cst.ENEMY_WALK_STATE

        level.check_will_fall(self)

    def go_die(self, how_to_die, direction=1):
        '''
        go_die方法，判断敌人以哪种方式狗带的总控方法
        :param how_to_die: 如何狗带
        :param direction: 方向
        :return: 无
        '''
        self.death_time = self.current_time
        if how_to_die in ['bumped', 'slide']:
            self.x_vel = cst.ENEMY_SPEED * direction
            self.y_vel = -8
            self.gravity = 0.6
            self.frame_index = 2
            self.state = 'die'
        elif how_to_die == cst.ENEMY_TRAMPLED_STATE:
            self.state = cst.ENEMY_TRAMPLED_STATE


class Goomba(Enemy):
    '''
    板栗仔
    '''
    def __init__(self, x, y_bottom, direction, name, color):
        self.name = 'goomba'
        bright_frame_rects = [(0, 16, 16, 16), (16, 16, 16, 16), (32, 16, 16, 16)]
        dark_frame_rects = [(96, 72, 16, 16), (16, 48, 16, 16), (32, 48, 16, 16)]

        if not color:
            frame_rects = bright_frame_rects
        else:
            frame_rects = dark_frame_rects

        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)

    def trampled(self, level):
        '''
        因为板栗仔会被踩扁，这里重写父类的trampled方法
        :param level: 关卡
        :return: 无
        '''
        self.x_vel = 0
        self.frame_index = 2
        if self.death_time == 0:
            self.death_time = self.current_time
        if self.current_time - self.death_time > 500:
            self.kill()


class Koopa(Enemy):
    '''
    库帕，就是乌龟怪
    '''
    def __init__(self, x, y_bottom, direction, name, color):
        self.name = 'koopa'
        bright_frame_rects = [(96, 9, 16, 22), (112, 9, 16, 22), (160, 9, 16, 22)]
        dark_frame_rects = [(96, 72, 16, 22), (112, 72, 16, 22), (160, 72, 16, 22)]

        if not color:
            frame_rects = bright_frame_rects
        else:
            frame_rects = dark_frame_rects

        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)
        self.shell_timer = 0

    def trampled(self, level):
        '''
        被踩扁
        :param level: level类，用到了其中的精灵组
        :return: 无
        '''
        self.x_vel = 0
        self.frame_index = 2

        if self.shell_timer == 0:
            self.shell_timer = self.current_time
        if self.current_time - self.shell_timer > 5000:
            self.state = cst.ENEMY_WALK_STATE
            self.x_vel = - cst.ENEMY_SPEED if self.direction == 0 else cst.ENEMY_SPEED
            level.enemy_group.add(self)
            level.shell_group.remove(self)
            self.shell_timer = 0

    def slide(self, level):
        pass
