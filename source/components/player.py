# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:28
@Auth ： Mars
@File ：player.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import tools, setup
from .. import const_var as cst
from . import powerup
import json
import os


class Player(pg.sprite.Sprite):
    def __init__(self, name):
        pg.sprite.Sprite.__init__(self)
        self.name = name
        self.setup_states()
        self.load_data()
        self.setup_velocities()
        self.setup_timers()
        self.load_imgs()
        self.cal_frame_duration()

    def load_data(self):
        '''
        载入人物的json文件（主要是抠图用的像素坐标和一些人物的基本属性）
        :return: 无
        '''
        file_name = self.name + '.json'
        file_path = os.path.join(cst.PLAYER_PATH, file_name)
        with open(file_path) as f:
            self.player_data = json.load(f)

    def setup_states(self):
        '''
        设定玩家状态
        :return: 无
        '''
        self.state = cst.PLAYER_STAND_STATE
        self.face_right = True
        self.dead = False
        self.big = False
        self.can_jump = True
        self.hurt_immune = False
        self.fire = False
        self.can_shoot = True

    def setup_velocities(self):
        '''
        人物运动相关（移动矢量速度， 加速度等）
        :return: 无
        '''
        speed = self.player_data['speed']    # 载入json中的默认速度（包括移动，奔跑的速度及加速度和转向加速度）
        self.x_vel = 0
        self.y_vel = 0

        self.max_walk_vel = speed['max_walk_speed']    # 最大移动速度
        self.max_run_vel = speed['max_run_speed']    # 最大奔跑速度
        self.max_y_vel = speed['max_y_velocity']    # y方向最大速度
        self.jump_vel = speed['jump_velocity']     # 跳跃速度
        self.walk_accel = speed['walk_accel']     # 移动加速度
        self.turn_accel = speed['turn_accel']    # 转向加速度
        self.run_accel = speed['run_accel']     # 奔跑加速度

        self.gravity = cst.GRAVITY    # 下落重力
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel
        self.anti_gravity = cst.ANTI_GRAVITY

    def setup_timers(self):
        '''
        用到的各类计时器
        :return: 无
        '''
        self.walking_timer = 0
        self.transition_timer = 0
        self.death_timer = 0
        self.hurt_immune_timer = 0
        self.last_fire_timer = 0

    def load_imgs(self):
        '''
        载入马里奥贴图（各种运动和状态帧）
        :return: 无
        '''
        sheet = setup.GRAPHICS[cst.MARIO_BROS]
        frame_rects = self.player_data['image_frames']    # 在先前载入的json文件中获取贴图的矩阵坐标

        # 下面定义了马里奥在右向（左向）时的普通状态，变大状态，加强状态
        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames,
        ]
        # 给定初始状态贴图
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames
        # 在这说明一下，载入的json文件在python中是字典类型
        for group, group_frame_rects in frame_rects.items():
            for frame_rect in group_frame_rects:
                right_image = tools.get_img(sheet, frame_rect['x'], frame_rect['y'],
                                            frame_rect['width'], frame_rect['height'],
                                            (0, 0, 0), cst.PLAYER_MULTI)
                left_image = pg.transform.flip(right_image, True, False)

                # 根据速度状态匹配贴图
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)

        self.frame_index = 0
        self.frames = self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self, keys, level):
        '''
        必备的update方法，更新玩家状态信息
        :param keys: 按键轮询
        :param level: 关卡
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        self.handle_states(keys, level)
        self.is_hurt_immune()

    def handle_states(self, keys, level):
        '''
        状态同一调度方法
        :param keys: 按键轮询
        :param level: 关卡
        :return: 无
        '''
        self.jump_or_not(keys)           # 是否处于跳起状态
        self.can_shoot_or_not(keys)      # 是否处于开火状态

        if self.state == cst.PLAYER_STAND_STATE:
            self.stand(keys, level)
        elif self.state == cst.PLAYER_WALK_STATE:
            self.walk(keys, level)
        elif self.state == cst.PLAYER_JUMP_STATE:
            self.jump(keys, level)
        elif self.state == cst.PLAYER_FALL_STATE:
            self.fall(keys, level)
        elif self.state == cst.PLAYER_DIE_STATE:
            self.die(keys)
        elif self.state == cst.PLAYER_SMALL_TO_BIG:
            self.small2big(keys)
        elif self.state == cst.PLAYER_BIG_TO_SMALL:
            self.big2small(keys)
        elif self.state == cst.PLAYER_BIG_TO_FIRE:
            self.big2fire(keys)
        elif self.state == cst.PLAYER_RAP:
            self.rap(keys)
        elif self.state == cst.PLAYER_BASKETBALL:    # 唱跳rap篮球 haha
            self.play_basketball(keys)

        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def jump_or_not(self, keys):
        '''
        判断是否处于跳跃状态
        :param keys: 按键
        :return: 无
        '''
        if not keys[pg.K_SPACE]:
            self.can_jump = True

    def stand(self, keys, level):
        '''
        静止状态
        :param keys: 按键
        :param level: 关卡
        :return: 无
        '''
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        if keys[pg.K_RIGHT]:    # 玩家通过按键操作时进入移动状态
            self.face_right = True
            self.state = cst.PLAYER_WALK_STATE
        elif keys[pg.K_LEFT]:
            self.face_right = False
            self.state = cst.PLAYER_WALK_STATE
        elif keys[pg.K_SPACE] and self.can_jump:
            self.state = cst.PLAYER_JUMP_STATE
            self.y_vel = self.jump_vel
        elif keys[pg.K_f]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def walk(self, keys, level):
        '''
        移动状态（可加速冲刺）
        :param keys: 按键
        :param level: 关卡
        :return: 无
        '''
        if keys[pg.K_f]:      # 玩家可通过f键来加速(后面的开火也是这个哦）
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
        else:    # 如果玩家未使用冲刺则按照正常速度来运动
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel
        if keys[pg.K_SPACE] and self.can_jump:
            self.state = cst.PLAYER_JUMP_STATE
            self.y_vel = self.jump_vel

        if self.current_time - self.walking_timer > self.cal_frame_duration():    # 运动帧切换
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
        if keys[pg.K_RIGHT]:    # 转向功能实现（附带一定惯性）
            self.face_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.cal_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pg.K_LEFT]:
            self.face_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.cal_vel(self.x_vel, self.x_accel, self.max_x_vel, False)

        else:    # 上面仅仅实现了马里奥大叔从静止状态到运动状态和运动状态之间的切换
            # 下面我们来实现让马里奥大叔从运动状态回到静止状态（很好实现，依靠判断速度矢量是否为零即可）
            if self.face_right:
                self.x_vel -= self.x_accel
                if self.x_vel < 0:
                    self.x_vel = 0
                    self.state = cst.PLAYER_STAND_STATE
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = cst.PLAYER_STAND_STATE

    def cal_vel(self, vel, accel, max_vel, is_face_right=True):
        '''
        动态计算速度矢量
        :param vel: 速度（矢量）
        :param accel: 加速度（矢量）
        :param max_vel: 最大速度（矢量）
        :param is_face_right: 人物朝向
        :return: 无
        '''
        if is_face_right:
            return min(vel + accel, max_vel)
        else:
            return max(vel - accel, -max_vel)

    def jump(self, keys, level):
        '''
        跳跃（实现小跳和大跳）
        :param keys: 按键
        :param level: 关卡
        :return: 无
        '''
        self.frame_index = 4
        self.y_vel += self.anti_gravity    # 马里奥反人类，有反重力效果
        self.can_jump = False

        if self.y_vel >= 0:
            self.state = cst.PLAYER_FALL_STATE    # 跳起后的状态就为下落

        # 解决马里奥空中转体（转向）
        if keys[pg.K_RIGHT]:
            self.x_vel = self.cal_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pg.K_LEFT]:
            self.x_vel = self.cal_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        elif keys[pg.K_f]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

        if not keys[pg.K_SPACE]:
            self.state = 'fall'

    def fall(self, keys, level):
        '''
        下落状态
        :param keys: 按键
        :param level: 关卡
        :return: 无
        '''
        self.y_vel = self.cal_vel(self.y_vel, self.gravity, self.max_y_vel)
        if keys[pg.K_RIGHT]:
            self.x_vel = self.cal_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pg.K_LEFT]:
            self.x_vel = self.cal_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        elif keys[pg.K_f]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def rap(self, keys):
        '''
        我是练习时常两年半的代码练习生，喜欢唱跳rap篮球，music！！！！
        :param keys:
        :return:
        '''
        pass

    def play_basketball(self, keys):
        pass

    def die(self, keys):
        '''
        实现死亡时的下落
        :param keys: 按键
        :return: 无
        '''
        self.rect.y += self.y_vel
        self.y_vel += self.anti_gravity

    def small2big(self, keys):
        '''
        马里奥吃了变异蘑菇能够变成巨型马里奥，那天板栗仔想起被巨人支配的恐惧
        :param keys: 按键
        :return: 无
        '''
        frame_duration = 65           # 每个变身阶段的帧持续时间
        sizes = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]   # 0 小， 1 中， 2 大
        frames_and_index = [(self.small_normal_frames, 0), (self.small_normal_frames, 7), (self.big_normal_frames, 0)]

        if self.transition_timer == 0:
            self.big = True
            self.transition_timer = self.current_time
            self.changing_index = 0
        elif self.current_time - self.transition_timer > frame_duration:
            self.transition_timer = self.current_time
            frames, index = frames_and_index[sizes[self.changing_index]]
            self.change_player_image(frames, index)
            self.changing_index += 1
            if self.changing_index == len(sizes):
                self.transition_timer = 0
                self.state = cst.PLAYER_WALK_STATE
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def big2small(self, keys):
        '''
        变身巨人的马里奥可不是无敌的
        :param keys: 按键
        :return: 无
        '''
        frame_duration = 65
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]   # 0 小， 1 中， 2 大
        frames_and_index = [(self.small_normal_frames, 8), (self.big_normal_frames, 8), (self.big_normal_frames, 4)]

        if self.transition_timer == 0:
            self.big = False
            self.transition_timer = self.current_time
            self.changing_index = 0
        elif self.current_time - self.transition_timer > frame_duration:
            self.transition_timer = self.current_time
            frames, index = frames_and_index[sizes[self.changing_index]]
            self.change_player_image(frames, index)
            self.changing_index += 1
            if self.changing_index == len(sizes):
                self.transition_timer = 0
                self.state = cst.PLAYER_WALK_STATE
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def big2fire(self, keys):
        '''
        巨型马里奥变身开火马里奥
        :param keys: 按键
        :return: 无
        '''
        frame_duration = 65
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_index = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]

        if self.transition_timer == 0:
            self.fire = True
            self.transition_timer = self.current_time
            self.changing_index = 0
        elif self.current_time - self.transition_timer > frame_duration:
            self.transition_timer = self.current_time
            frames, index = frames_and_index[sizes[self.changing_index]]
            self.change_player_image(frames, index)
            self.changing_index += 1
            if self.changing_index == len(sizes):
                self.transition_timer = 0
                self.state = cst.PLAYER_WALK_STATE
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames

    def change_player_image(self, frames, index):
        '''
        根据玩家速度方向给定马里奥左右朝向的贴图
        :param frames: 贴图帧
        :param index: 帧索引
        :return: 无
        '''
        self.frame_index = index
        if self.face_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx

    def go_die(self):
        '''
        实现死亡时的小跳
        :return: 无
        '''
        self.dead = True
        self.y_vel = self.jump_vel
        self.frame_index = 6
        self.state = 'die'
        self.death_timer = self.current_time

    def cal_frame_duration(self):
        '''
        根据马里奥的速度来动态分配帧切换速率
        :return: 无
        '''
        duration = -60 / self.max_run_vel * abs(self.x_vel) + 75
        return duration

    def is_hurt_immune(self):
        '''
        判断当前马里奥是否处于无敌状态
        :return: 无
        '''
        if self.hurt_immune:
            if self.hurt_immune_timer == 0:
                self.hurt_immune_timer = self.current_time
                self.blank_image = pg.Surface((1, 1))
            elif self.current_time - self.hurt_immune_timer < 2000:
                if (self.current_time - self.hurt_immune_timer) % 100 < 50:
                    self.image = self.blank_image
            else:
                self.hurt_immune = False
                self.hurt_immune_timer = 0

    def shoot_fireball(self, level):
        '''
        开火！！！
        :param level: 关卡
        :return: 无
        '''
        if self.current_time - self.last_fire_timer > 300:
            self.frame_index = 6
            self.fireball = powerup.Fireball(self.rect.centerx, self.rect.centery, self.face_right)
            level.powerup_group.add(self.fireball)
            self.can_shoot = False
            self.last_fire_timer = self.current_time

    def can_shoot_or_not(self, keys):
        '''
        是否可以开火
        :param keys: 按键
        :return: 无
        '''
        if not keys[pg.K_f]:
            self.can_shoot = True