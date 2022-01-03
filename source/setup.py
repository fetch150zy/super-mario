# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:34
@Auth ： Mars
@File ：setup.py
@IDE ：PyCharm
"""

import pygame as pg
from . import tools, const_var as cst
import os

pg.init()                                          # 初始化
SCREEN = pg.display.set_mode(cst.SCREEN_SIZE)      # 图层
pg.display.set_caption(cst.ORIGINAL_CAPTION)       # 标题

# 素材包
GRAPHICS = tools.load_graphics('resources/graphics')
