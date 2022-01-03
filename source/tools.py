# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:35
@Auth ： Mars
@File ：tools.py
@IDE ：PyCharm
"""
import os

import pygame as pg
import random, sys
from . import const_var as cst


class Game:
    '''
    游戏主调类
    '''
    def __init__(self, state_dict, start_state):
        self.screen = pg.display.get_surface()        # 游戏图层
        self.clock = pg.time.Clock()                  # 游戏时钟
        self.keys = pg.key.get_pressed()              # 按键轮询
        self.state_dict = state_dict                  # 游戏状态表
        self.state = self.state_dict[start_state]     # 游戏状态（初始为菜单界面）

    def update(self):
        '''
        调用各个状态的update方法，实现各个状态信息的实时更新
        :return: 无
        '''
        if self.state.finished:
            game_info = self.state.game_info
            next_state = self.state.next
            self.state.finshed = False
            self.state = self.state_dict[next_state]
            self.state.start(game_info)
        self.state.update(self.screen, self.keys)

    def run(self):
        '''
        游戏主循环
        :return: 无
        '''
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    quit()
                elif event.type == pg.KEYDOWN:
                    self.keys = pg.key.get_pressed()
                elif event.type == pg.KEYUP:
                    self.keys = pg.key.get_pressed()
            self.update()

            pg.display.update()
            self.clock.tick(60)


def load_graphics(path, accept=cst.RESOURCE_FORMAT):
    '''
    导入素材包
    :param path: 素材包路径
    :param accept: 接受文件格式
    :return: 处理后的素材（字典类型，素材名：素材）
    '''
    graphics = {}
    for picture in os.listdir(path):             # 将文件名和拓展名分开
        name, ext = os.path.splitext(picture)    # 匹配正确后缀的文件
        if ext.lower() in accept:                # 拼接路径
            img = pg.image.load(os.path.join(path, picture))
            if img.get_alpha():                  # 有透明图层的
                img = img.convert_alpha()
            else:                                # 无透明图层
                img = img.convert()
            graphics[name] = img
    return graphics


def get_img(sheet, x, y, width, height, color_key, scale):
    '''
    处理素材包的图片
    :param sheet: 图层
    :param x: x坐标
    :param y: y坐标
    :param width: 宽度
    :param height: 高度
    :param color_key: 颜色
    :param scale: 缩放比
    :return: 处理后的图层
    '''
    image = pg.Surface((width, height))
    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(color_key)
    image = pg.transform.scale(image, (int(width*scale), int(height*scale)))
    return image
