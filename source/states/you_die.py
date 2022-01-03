# -*- coding: utf-8 -*-
"""
@Time ： 28/11/2021 下午4:20
@Auth ： Mars
@File ：you_die.py
@IDE ：PyCharm
"""

import pygame as pg
from .. components import info
from . import load_screen
from .. import const_var as cst


class YouDie(load_screen.LoadScreen):
    '''
    玩家死亡且生命数不为0时显示死亡信息
    '''
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = cst.STATE_LEVEL        # 下一阶段为关卡
        self.duration = cst.LOAD_SCREEN_DURATION
        self.timer = 0
        self.info = info.Info(cst.STATE_YOU_DIE, self.game_info)
