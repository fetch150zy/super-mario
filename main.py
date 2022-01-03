# -*- coding: utf-8 -*-
"""
@Time ： 16/11/2021 下午9:12
@Auth ： Mars
@File ：main.py
@IDE ：PyCharm
"""
from source import tools
from source.states import main_menu, load_screen, level, game_over, time_out, you_die, you_win
from source import const_var as cst


def main():
    # 游戏状态表
    state_dict = {
        cst.STATE_MAIN_MENU: main_menu.MainMenu(),            # 初始菜单界面
        cst.STATE_LOAD_SCREEN: load_screen.LoadScreen(),      # 载入界面
        cst.STATE_LEVEL: level.Level(),                       # 关卡
        cst.STATE_GAME_OVER: game_over.GameOver(),            # 游戏结束
        cst.STATE_TIME_OUT: time_out.TimeOut(),               # 时间耗尽
        cst.STATE_YOU_DIE: you_die.YouDie(),                   # 死亡
        cst.STATE_YOU_WIN: you_win.YouWin(),                    # 通关
    }
    game = tools.Game(state_dict, cst.START_STATE)
    game.run()


if __name__ == "__main__":
    main()
