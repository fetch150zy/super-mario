# -*- coding: utf-8 -*-
"""
@Time ： 22/11/2021 下午8:28
@Auth ： Mars
@File ：main_menu.py
@IDE ：PyCharm
"""

import pygame as pg
from .. import setup, tools
from .. import const_var as cst
from ..components import info


class MainMenu:
    '''
    游戏菜单界面
    '''
    def __init__(self):
        self.game_info = {       # 游戏中的数据
            cst.GAIN_SCORES: 0,          # 得分
            cst.GAIN_COINS: 0,           # 金币
            cst.PLAYER_LIVES: cst.EASY_GAME_LIVES,             # 生命数
            cst.PLAYER_STATE: cst.MARIO_START_STATE,    # 马里奥大叔状态
            cst.EASY_OR_HARD: cst.EASY_GAME,                 # 游戏难度
            cst.REMAINING_TIME: int(cst.TIME_OUT_DURATION / 1000),    # 游戏时间限制
        }
        self.start(self.game_info)

    def start(self, game_info):
        '''
        :param game_info: 游戏数据
        :return: 无
        '''
        self.reset_game_info()
        self.game_info = game_info
        self.setup_bg()               # 菜单界面背景
        self.setup_player()           # 菜单界面角色（只是个贴图，无法操作）
        self.setup_cursor()           # 菜单界面光标（用于选择 easy game 还是 hard game）
        self.info = info.Info(cst.STATE_MAIN_MENU, self.game_info)      # 调用Info类实现文本显示和更新功能
        self.finished = False                   # 初始菜单界面的flag标志，为True时该游戏阶段结束进入下一阶段
        self.next = cst.STATE_LOAD_SCREEN       # 下一阶段为载入阶段

    def setup_bg(self):
        '''
        设置菜单界面的背景
        :return: 无
        '''
        self.bg = setup.GRAPHICS[cst.LEVEL_1]
        self.bg_rect = self.bg.get_rect()
        self.bg = pg.transform.scale(self.bg, (int(self.bg_rect.width * cst.BG_MULTI),
                                               int(self.bg_rect.height * cst.BG_MULTI)))
        self.view_port = setup.SCREEN.get_rect()
        self.caption = tools.get_img(setup.GRAPHICS[cst.TITLE_SCREEN], 1, 60, 176, 88, (255, 0, 220), cst.BG_MULTI)

    def setup_player(self):
        '''
        马里奥人物贴图
        :return: 无
        '''
        self.player_img = tools.get_img(setup.GRAPHICS[cst.MARIO_BROS], 178, 32, 12, 16, (0, 0, 0), cst.PLAYER_MULTI)

    def setup_cursor(self):
        '''
        游戏光标（其实就是马里奥中的那个蘑菇 ^a^ ）
        :return: 无
        '''
        self.cursor = pg.sprite.Sprite()
        self.cursor.image = tools.get_img(setup.GRAPHICS[cst.ITEM_OBJECTS], 25, 160, 8, 8, (0, 0, 0), cst.PLAYER_MULTI)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 360)
        self.cursor.rect = rect
        self.cursor.state = cst.EASY_GAME    # 状态机（主要用于判断当前用户选择了哪种游戏难度）

    def update_cursor(self, keys):
        '''
        更新光标，玩家可选择难度
        :param keys: 按键轮询
        :return: 无
        '''
        if keys[pg.K_UP]:
            self.cursor.state = cst.EASY_GAME
            self.cursor.rect.y = 360    # 移动光标哈，来选择你的英雄（/doge）
            self.game_info[cst.EASY_OR_HARD] = cst.EASY_GAME
        elif keys[pg.K_DOWN]:
            self.cursor.state = cst.HARD_GAME
            self.cursor.rect.y = 405
            self.game_info[cst.EASY_OR_HARD] = cst.HARD_GAME
        elif keys[pg.K_RETURN]:         # 按回车就会进入加载界面然后就可以开始游戏啦
            self.judge_easy_hard()
            if self.cursor.state == cst.EASY_GAME:
                self.finished = True
            elif self.cursor.state == cst.HARD_GAME:
                self.finished = True

    def update(self, surface, keys):
        '''
        更新文本信息并显示载入的贴图
        :param surface: 图层
        :param keys: 按键轮询
        :return: 无
        '''
        self.update_cursor(keys)
        surface.blit(self.bg, self.view_port)         # 背景
        surface.blit(self.caption, (170, 100))        # 标题
        surface.blit(self.player_img, (100, 490))     # 人物
        surface.blit(self.cursor.image, self.cursor.rect)    # 光标

        self.info.update()
        self.info.draw(surface)

    def reset_game_info(self):
        '''
        写这个方法主要用来重载游戏基本数据（就是你game_over了，你上一局的数据不会保留）
        :return: 无
        '''
        self.game_info.update(
            {
                cst.GAIN_SCORES: 0,
                cst.GAIN_COINS: 0,
                cst.PLAYER_LIVES: cst.EASY_GAME_LIVES,
                cst.PLAYER_STATE: cst.MARIO_START_STATE,
                cst.EASY_OR_HARD: cst.EASY_GAME,
                cst.REMAINING_TIME: int(cst.TIME_OUT_DURATION / 1000),
            }
        )

    def judge_easy_hard(self):
        '''
        判断当前游戏状态是easy还是hard
        :return: 无
        '''
        if self.game_info[cst.EASY_OR_HARD] == cst.EASY_GAME:
            self.game_info[cst.PLAYER_LIVES] = cst.EASY_GAME_LIVES
        else:
            self.game_info[cst.PLAYER_LIVES] = cst.HARD_GAME_LIVES

