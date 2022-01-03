# -*- coding: utf-8 -*-
"""
@Time ： 24/11/2021 下午8:55
@Auth ： Mars
@File ：game_over.py
@IDE ：PyCharm
"""

import pygame as pg
from .. components import info
from . import load_screen
from .. import const_var as cst


class GameOver(load_screen.LoadScreen):
    '''
    游戏结束，把游戏结束的信息打印到界面上，并返回菜单界面
    '''
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = cst.STATE_MAIN_MENU
        self.duration = cst.LOAD_SCREEN_DURATION
        self.timer = 0
        self.info = info.Info(cst.STATE_GAME_OVER, self.game_info)

