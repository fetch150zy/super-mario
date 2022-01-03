# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:28
@Auth ： Mars
@File ：info.py
@IDE ：PyCharm
"""

import pygame as pg
import pygame.font
from .. import const_var as cst
from . import coin
from .. import setup, tools


pygame.font.init()


class Info:
    '''
    这个Info类主要用于实现一些信息的显示和更新
    '''
    def __init__(self, state, game_info):
        '''
        :param state: 游戏当前状态（阶段）
        :param game_info: 游戏信息
        '''
        self.world_info = {
            cst.STATE_MAIN_MENU: 'menu',
            cst.STATE_LOAD_SCREEN: '1 - 1',
            cst.STATE_LEVEL: '1 - 1',
            cst.STATE_GAME_OVER: '1 - 1',
            cst.STATE_TIME_OUT: '1 - 1',
            cst.STATE_YOU_DIE: '1 - 1',
            cst.STATE_YOU_WIN: '1 - 1'
        }
        self.state = state            # 状态（阶段）
        self.game_info = game_info    # 游戏信息
        self.create_state_labels()    # 创建状态标签
        self.create_info_labels()     # 创建信息标签
        self.flash_coin = coin.FlashCoin()    # 闪烁的金币

    def create_state_labels(self):
        '''
        用于在图层上显示当前游戏状态的文本信息
        :return: 无
        '''
        self.state_labels = []
        if self.state == cst.STATE_MAIN_MENU:        # 菜单界面
            self.state_labels.append((self.create_label(cst.CHOICE_GAME_EASY), (272, 360)))
            self.state_labels.append((self.create_label(cst.CHOICE_GAME_HARD, font_color=cst.RED), (272, 405)))
            self.state_labels.append((self.create_label(cst.RANK_LABEL), (260, 465)))
            self.state_labels.append((self.create_label(cst.RANK_INFO), (410, 465)))
        elif self.state == cst.STATE_GAME_OVER:      # 游戏结束
            self.state_labels.append((self.create_label(cst.GAME_OVER_LABEL, size=100, font_color=cst.RED), (130, 280)))
        elif self.state == cst.STATE_LOAD_SCREEN or self.state == cst.STATE_TIME_OUT or self.state == cst.STATE_YOU_DIE:
            self.state_labels.append((self.create_label(cst.WORLD_LABEL), (280, 200)))
            self.state_labels.append((self.create_label(self.world_info[self.state]), (430, 200)))
            self.state_labels.append((self.create_label(cst.LIVES_LABEL.format(self.game_info[cst.PLAYER_LIVES])), (380, 280)))
            self.player_img = tools.get_img(setup.GRAPHICS[cst.MARIO_BROS], 178, 32, 12, 16, (0, 0, 0), cst.BG_MULTI)
            if self.state == cst.STATE_LOAD_SCREEN:      # 载入界面
                self.state_labels.append((self.create_label(cst.JOKE_INFO_1, font_color=cst.CYAN), (40, 340)))
                self.state_labels.append((self.create_label(cst.JOKE_INFO_2, font_color=cst.CYAN), (90, 400)))
            elif self.state == cst.STATE_TIME_OUT:       # 时间耗尽
                self.state_labels.append((self.create_label(cst.TIME_OUT_LABEL, font_color=cst.BLUE), (320, 360)))
            elif self.state == cst.STATE_YOU_DIE:        # 玩家死亡但未耗尽生命
                self.state_labels.append((self.create_label(cst.YOU_DIE_LABEL, font_color=cst.RED), (320, 360)))
        elif self.state == cst.STATE_YOU_WIN:            # 通关
            self.state_labels.append((self.create_label(cst.YOU_WIN_LABEL, size=100, font_color=cst.GREEN), (220, 280)))

    def create_info_labels(self):
        '''
        这些文字信息贯彻游戏始终
        '''
        self.info_labels = []
        if not self.state == cst.STATE_YOU_WIN and not self.state == cst.STATE_GAME_OVER:    # 游戏通关和结束时加载界面不显示这些信息
            self.info_labels.append((self.create_label(cst.SCORE_LABEL), (75, 30)))
            self.info_labels.append((self.create_label(cst.WORLD_LABEL), (450, 30)))
            self.info_labels.append((self.create_label(cst.TIME_LABEL), (625, 30)))
            self.info_labels.append((self.create_label('{0:03}'.format(self.game_info[cst.REMAINING_TIME])), (640, 65)))
            self.info_labels.append((self.create_label('{0:06}'.format(self.game_info[cst.GAIN_SCORES])), (75, 65)))
            self.info_labels.append((self.create_label('x{0:02}'.format(self.game_info[cst.GAIN_COINS])), (300, 55)))
            self.info_labels.append((self.create_label(self.world_info[self.state]), (470, 65)))

    def create_label(self, label, size=cst.FONT_SIZE, width_scale=cst.WIDTH_SCALE, height_scale=cst.HEIGHT_SCALE, font_color=cst.WHITE):
        '''
        创建文本信息标签
        :param label: 文本
        :param size: 字体大小，默认40
        :param width_scale: 宽度缩放，默认1.25
        :param height_scale: 高度缩放，默认1.15
        :param font_color: 字体颜色，默认白色
        :return: 处理后的字体
        '''
        font = pg.font.SysFont(cst.FONT, size)
        label_img = font.render(label, True, font_color)    # 增加文字锯齿感（效果不佳，采用下面这种处理方式）
        rect = label_img.get_rect()
        label_img = pg.transform.scale(label_img, (int(rect.width * width_scale),
                                                   int(rect.height * height_scale)))
        return label_img

    def update(self):
        '''
        实现金币闪烁的功能，在FlashCoin类中具体实现
        完成实时刷新文本信息的功能
        :return: 无
        '''
        if not self.state == cst.STATE_YOU_WIN and not self.state == cst.STATE_GAME_OVER:
            self.flash_coin.update()
            self.create_info_labels()
            self.create_state_labels()

    def draw(self, surface):
        '''
        把文本和图片绘制在图层上
        :param surface: 图层
        :return: 无
        '''
        for label in self.state_labels:
            surface.blit(label[0], label[1])

        for label in self.info_labels:
            surface.blit(label[0], label[1])

        # 游戏通关和结束时加载界面不显示这些信息
        if not self.state == cst.STATE_YOU_WIN and not self.state == cst.STATE_GAME_OVER:
            surface.blit(self.flash_coin.image, self.flash_coin.rect)

        if self.state == cst.STATE_LOAD_SCREEN or self.state == cst.STATE_YOU_DIE or self.state == cst.STATE_TIME_OUT:
            surface.blit(self.player_img, (300, 270))
