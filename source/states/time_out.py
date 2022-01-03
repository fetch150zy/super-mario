# -*- coding: utf-8 -*-
"""
@Time ： 28/11/2021 上午11:48
@Auth ： Mars
@File ：time_out.py
@IDE ：PyCharm
"""


import pygame as pg
from .. components import info
from . import load_screen
from .. import const_var as cst


class TimeOut(load_screen.LoadScreen):
    '''
    时间耗尽时显示时间耗尽的信息并减少一条生命（简单模式下生命数为零就狗带），困难模式下直接狗带
    '''
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = cst.STATE_LEVEL      # 下一阶段仍为关卡
        self.duration = cst.LOAD_SCREEN_DURATION
        self.timer = 0
        self.info = info.Info(cst.STATE_TIME_OUT, self.game_info)
