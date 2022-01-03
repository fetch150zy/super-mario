# -*- coding: utf-8 -*-
"""
@Time ： 22/11/2021 下午8:29
@Auth ： Mars
@File ：load_screen.py
@IDE ：PyCharm
"""

import pygame as pg
from .. components import info
from .. import const_var as cst


class LoadScreen:
    '''
    载入界面（完成一些显示和更新的操作）
    '''
    def start(self, game_info):
        '''
        :param game_info: 共享游戏数据
        :return: 无
        '''
        self.game_info = game_info
        self.finished = False
        self.next = cst.STATE_LEVEL        # 下一阶段为关卡
        self.timer = 0               # 载入界面计时器（主要用于设置载入界面的加载时间）
        self.info = info.Info(cst.STATE_LOAD_SCREEN, self.game_info)    # 在载入界面显示一些文字信息
        self.duration = cst.LOAD_SCREEN_DURATION        # 载入界面持续时间

    def update(self, surface, keys):
        '''
        更新状态
        :param surface: 图层
        :param keys: 按键轮询
        :return: 无
        '''
        self.draw(surface)
        if self.timer == 0:                                       # 开始载入
            self.timer = pg.time.get_ticks()
        elif pg.time.get_ticks() - self.timer > self.duration:    # 2秒后载入结束
            self.finished = True                                  # 更新flag标志（表示当前状态结束，顺利进入下一阶段）
            self.timer = 0
        self.info.update()

    def draw(self, surface):
        '''
        绘制图层
        :param surface: 图层
        :return: 无
        '''
        surface.fill((0, 0, 0))
        self.info.draw(surface)
