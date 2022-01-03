# -*- coding: utf-8 -*-
"""
@Time ： 22/11/2021 下午8:29
@Auth ： Mars
@File ：level.py
@IDE ：PyCharm
"""
# 这个文件用于实现关卡
import pygame as pg
from .. components import info, player, stuff, brick, box, enemy, powerup as pu, coin
from .. import tools, setup
from .. import const_var as cst
import os, json


class Level:
    '''
    游戏关卡
    '''
    def start(self, game_info):
        self.game_info = game_info    # 游戏数据
        self.duration = cst.TIME_OUT_DURATION    # 关卡时间限制
        self.timer = 0                # 计时器
        self.finished = False         # 状态标志
        self.next = cst.STATE_GAME_OVER     # 下一状态
        self.info = info.Info(cst.STATE_LEVEL, self.game_info)  # 文本信息
        self.score_list = []   # 得分表单
        self.game_win_time = 0  # 游戏结束延时计时器

        self.load_map_data()          # 载入地图json文件
        self.setup_bg()               # 背景
        self.setup_start_pos()        # 马里奥大叔出生位置
        self.setup_player()           # 马里奥大叔实时坐标
        self.setup_ground_items()     # 设定地面杂项（水管，台阶啥的）
        self.setup_brick_and_box()    # 设定砖块和宝箱
        self.setup_enemies()          # 设定敌人
        self.setup_flagpole()         # 旗帜
        self.setup_castle_flag()      # 城堡旗帜
        self.setup_checkpoints()      # 设定检查点（用于触发敌人）

    def load_map_data(self):
        '''
        载入第一关中的要用到的数据（json）
        :return: 无
        '''
        file_name = cst.LEVEL_1 + '.json'
        file_path = os.path.join(cst.MAP_PATH, file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_start_pos(self):
        '''
        设置马里奥大叔的出生位置（每次死亡也会回到这个位置）以及地图的start_x和end_x
        :return: 无
        '''
        self.pos = []
        for data in self.map_data['maps']:
            self.pos.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
        self.start_x, self.end_x, self.player_x, self.player_y = self.pos[0]

    def setup_bg(self):
        '''
        设置背景（关卡背景）
        :return: 无
        '''
        self.image_name = self.map_data['image_name']
        self.bg = setup.GRAPHICS[self.image_name]
        rect = self.bg.get_rect()
        self.bg = pg.transform.scale(self.bg, (int(rect.width * cst.BG_MULTI),
                                               int(rect.height * cst.BG_MULTI)))
        self.bg_rect = self.bg.get_rect()
        self.game_window = setup.SCREEN.get_rect()
        self.game_ground = pg.Surface((self.bg_rect.width, self.bg_rect.height))

    def setup_player(self):
        '''
        载入马里奥大叔的贴图并设定在地图上的位置
        :return: 无
        '''
        self.player = player.Player('mario')
        self.player.rect.x = self.game_window.x + self.player_x
        self.player.rect.bottom = self.player_y

    def setup_ground_items(self):
        '''
        设定地图上出现的水管，地面，台阶等基本对象
        :return:
        '''
        self.ground_items_group = pg.sprite.Group()
        for name in ['ground', 'pipe', 'step']:
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'], item['y'],  item['width'], item['height'], name))

    def update(self, surface, keys):
        '''
        每个状态必备的update函数（实现实时更新数据）
        :param surface: 图层
        :param keys: 按键轮询
        :return: 无
        '''
        self.current_time = pg.time.get_ticks()
        self.player.update(keys, self)
        self.is_timeout()       # 判断当前是否时间耗尽

        if self.player.dead:
            if self.current_time - self.player.death_timer > cst.DEAD_DURATION:
                self.finished = True
                self.update_game_info()    # 更新生命信息（很重要，因为你死了就要减少一条生命）
        elif self.is_frozen():             # 角色变身时游戏世界是静止的
            pass
        else:                              # 没死
            self.update_player_pos()    # 玩家位置
            self.check_checkpoints()    # 检查点
            self.check_if_go_die()      # 是否要死亡
            self.update_game_window()   # 游戏窗体
            self.info.update()          # 游戏文本信息
            self.brick_group.update()   # 砖块
            self.box_group.update()     # 宝箱
            self.enemy_group.update(self)    # 敌人（活着的）
            self.dead_group.update(self)     # 敌人（死了的）
            self.shell_group.update(self)    # 龟壳（被玩家踩了的koopa）
            self.coin_group.update(self)         # 金币
            self.powerup_group.update(self)  # 道具
            self.flag_group.update()         # 城堡上旗帜
            self.flagpole_group.update()     # 旗帜
            for score in self.score_list:     # 得分
                score.update(self.score_list)
            self.delay_win()        # 到达终点时延时两秒才进入加载界面

        self.draw(surface)

    def is_frozen(self):
        '''
        时间冻结大法
        :return: 玩家是否处于变身状态
        '''
        return self.player.state in ['small2big', 'big2small', 'big2fire', 'fire2small']

    def update_player_pos(self):
        '''
        更新玩家在地图上的位置
        :return: 无
        '''
        # 保证玩家不出界（x方向）
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_x_collisions()        # 碰撞检测（x方向）
        if not self.player.dead:         # 加这个判断的原因是玩家如果狗带的话就不再进行碰撞检测
            self.player.rect.y += self.player.y_vel
            self.check_y_collisions()    # 碰撞检测（y方向）

    def check_x_collisions(self):
        '''
        把水管，地面，台阶，砖块，宝箱都加到碰撞检测精灵组中
        :return: 无
        '''
        check_group = pg.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided_sprite = pg.sprite.spritecollideany(self.player, check_group)
        if collided_sprite:     # 如果玩家和水管，地面，台阶，砖块，宝箱有碰撞就调整玩家位置
            self.adjust_player_x(collided_sprite)

        if self.player.hurt_immune:      # 玩家由加强状态变为非加强状态时提供一定的无敌时间
            return

        # 玩家与敌人的碰撞单独来判断
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:
            if self.player.big:              # 如果玩家是加强状态就变小
                self.player.state = cst.PLAYER_BIG_TO_SMALL
                self.game_info[cst.PLAYER_STATE] = 'small'
                self.player.hurt_immune = True    # 变大效果结束时有一段无敌时间
            else:                            # 如果本来就是small状态，那就狗带
                self.player.go_die()

        # koopa被玩家踩后会变成龟壳（单独来判断）
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)
        if shell:
            if shell.state == cst.ENEMY_SLIDE_STATE:          # 龟壳是滑行状态
                if self.player.big:             # 如果玩家是加强状态就变小
                    self.player.state = cst.PLAYER_BIG_TO_SMALL
                    self.game_info[cst.PLAYER_STATE] = 'small'
                    self.player.hurt_immune = True
                else:                           # 如果本来就是small状态，那就狗带
                    self.player.go_die()
            else:                               # 不是滑行状态， 玩家可以把龟壳激发为滑行状态
                self.update_score(200, shell, coin_num=0)
                if self.player.rect.x < shell.rect.x:     # 方向判定
                    shell.x_vel = 10
                    shell.rect.x += 40
                    shell.direction = 1
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 40
                    shell.direction = 0
                shell.state = cst.ENEMY_SLIDE_STATE

        # 玩家与道具的碰撞检测
        powerup = pg.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            if powerup.name == 'mushroom':
                self.update_score(1000, powerup, coin_num=0)
                if self.game_info[cst.PLAYER_STATE] == 'small':
                    self.player.state = cst.PLAYER_SMALL_TO_BIG
                    self.game_info[cst.PLAYER_STATE] = 'big'
                powerup.kill()
            if powerup.name == 'fireball':
                pass
            if powerup.name == 'fireflower':
                self.update_score(1000, powerup, coin_num=0)
                if self.game_info[cst.PLAYER_STATE] == 'big':
                    self.player.state = cst.PLAYER_BIG_TO_FIRE
                    self.game_info[cst.PLAYER_STATE] = 'fire'
                elif self.game_info[cst.PLAYER_STATE] == 'small':
                    self.player.state = cst.PLAYER_SMALL_TO_BIG
                    self.game_info[cst.PLAYER_STATE] = 'big'
                elif self.game_info[cst.PLAYER_STATE] == 'fire':
                    pass
                else:
                    pass
                powerup.kill()

    def adjust_player_x(self, sprite):
        '''
        调整玩家x方向位置
        :param sprite: 与玩家碰撞的精灵（水管，地面，台阶，砖块，宝箱等）
        :return: 无
        '''
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.left
        else:
            self.player.rect.left = sprite.rect.right
        self.player.x_vel = 0

    def check_y_collisions(self):
        '''
        y方向碰撞检测
        :return: 无
        '''
        ground_item = pg.sprite.spritecollideany(self.player, self.ground_items_group)  # 玩家与地面，台阶，管道的碰撞检测
        brick = pg.sprite.spritecollideany(self.player, self.brick_group)               # 与砖块
        box = pg.sprite.spritecollideany(self.player, self.box_group)                   # 与宝箱
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)               # 与敌人

        # 下面是一个简单的判定玩家是顶到了砖块还是宝箱
        if brick and box:
            to_brick = abs(self.player.rect.centerx - brick.rect.centerx)
            to_box = abs(self.player.rect.centerx - box.rect.centerx)
            if to_brick > to_box:
                brick = None
            else:
                box = None

        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:
            self.enemy_group.remove(enemy)  # 把敌人移出碰撞检测组
            if self.player.hurt_immune:       # 无敌
                self.update_score(100, enemy, coin_num=0)
                how_to_die = cst.ENEMY_BUMPED_STATE
                self.dead_group.add(enemy)
                enemy.go_die(how_to_die, 1 if self.player.face_right else -1)
                return
            if enemy.name == 'koopa':         # 如果是小乌龟，就变成龟壳
                self.shell_group.add(enemy)
            else:                             # 否则就让敌人狗带，并加到死的敌人组
                self.update_score(100, enemy, coin_num=0)
            self.dead_group.add(enemy)
            if self.player.y_vel < 0:       # 如果玩家是跳起状态（特指起跳过程），敌人是被顶翻的
                how_to_die = cst.ENEMY_BUMPED_STATE
            else:                           # 否则玩家是下落的，敌人就是被踩死的
                how_to_die = cst.ENEMY_TRAMPLED_STATE
                self.player.state = cst.PLAYER_JUMP_STATE
                self.player.rect.bottom = enemy.rect.top         # 这边是实现玩家踩到敌人有一个小跳的动作
                self.player.y_vel = self.player.jump_vel * 0.7
            enemy.go_die(how_to_die, 1 if self.player.face_right else -1)
        self.check_will_fall(self.player)                        # 下落检测

    def adjust_player_y(self, sprite):
        '''
        调整y方向位置
        :param sprite: 碰撞精灵
        :return: 无
        '''
        if self.player.rect.bottom < sprite.rect.bottom:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = cst.PLAYER_WALK_STATE
        else:
            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = cst.PLAYER_FALL_STATE

            self.is_enemy_on(sprite)      # 判断是否有敌人在砖块，宝箱之类的上面

            if sprite.name == 'box':         # 玩家顶的是宝箱（宝箱小跳一下然后复位，之后就不能顶了）
                if sprite.state == cst.BOX_REST_STATE:
                    sprite.go_bumped()
            if sprite.name == 'brick':       # 玩家顶的是砖块，小跳一下复位，可以一直顶
                if self.player.big and sprite.brick_type == 0:     # 如果玩家是变大状态并且砖块类型正确，可以顶碎
                    sprite.smashed(self.dead_group)
                elif sprite.state == cst.BRICK_REST_STATE:
                    sprite.go_bumped()
                else:
                    pass

    def is_enemy_on(self, sprite):
        '''
        判断是否有敌人在砖块，宝箱之上
        :param sprite: 障碍物
        :return: 无
        '''
        sprite.rect.y -= 1          # 试探性上移一个像素然后检测是否与敌人有碰撞（和检测下落的思路一致）
        enemy = pg.sprite.spritecollideany(sprite, self.enemy_group)
        if enemy:                   # 如果有碰撞，敌人就被顶翻
            self.update_score(100, enemy, coin_num=0)
            self.enemy_group.remove(enemy)
            self.dead_group.add(enemy)
            if sprite.rect.centerx > enemy.rect.centerx:    # 顶翻朝向的简单区分
                enemy.go_die('bumped', -1)
            else:
                enemy.go_die('bumped', 1)
        sprite.rect.y += 1

    def check_will_fall(self, sprite):
        '''
        下落判断
        :param sprite: 精灵（可以是玩家，也可以是敌人）
        :return: 无
        '''
        sprite.rect.y += 1           # 试探性下降一像素，来判断脚下是否为空
        check_group = pg.sprite.Group(self.ground_items_group, self.box_group, self.brick_group)
        collided = pg.sprite.spritecollideany(sprite, check_group)
        if not collided and sprite.state != 'jump' and not self.is_frozen():  # 不允许玩家在上一次跳结束之前再次起跳
            sprite.state = 'fall'
        sprite.rect.y -= 1

    def update_game_window(self):
        '''
        这里主要实现了当玩家越过屏幕三分之一时才会移动地图（还把地图边缘限制死了）
        :return: 无
        '''
        third = self.game_window.x + self.game_window.width / 3
        if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x:
            self.game_window.x += self.player.x_vel
        elif self.player.x_vel < 0 and self.player.rect.centerx < third * 2 and self.game_window.left > self.start_x \
                and self.game_window.right < self.end_x:
            self.game_window.x += self.player.x_vel

    def draw(self, surface):
        '''
        绘制图层
        :param surface: 图层
        :return: 无
        '''
        self.game_ground.blit(self.bg, self.game_window, self.game_window)
        self.game_ground.blit(self.player.image, self.player.rect)
        self.powerup_group.draw(self.game_ground)      # 道具
        self.brick_group.draw(self.game_ground)        # 砖块
        self.box_group.draw(self.game_ground)          # 宝箱
        self.enemy_group.draw(self.game_ground)        # 活着的敌人
        self.dead_group.draw(self.game_ground)         # 死亡敌人
        self.shell_group.draw(self.game_ground)        # 龟壳
        self.coin_group.draw(self.game_ground)         # 金币
        self.flag_group.draw(self.game_ground)         # 城堡旗帜
        self.flagpole_group.draw(self.game_ground)     # 旗帜
        for score in self.score_list:                  # 得分
            score.draw(self.game_ground)

        surface.blit(self.game_ground, (0, 0), self.game_window)
        self.info.draw(surface)                        # 文本

    def check_if_go_die(self):
        '''
        掉出地图便判定死亡
        :return: 无
        '''
        if self.player.rect.y > cst.SCREEN_HEIGHT:
            self.player.go_die()

    def update_game_info(self):
        '''
        更新玩家生命和时间
        :return: 无
        '''
        self.game_info[cst.REMAINING_TIME] = int(cst.TIME_OUT_DURATION / 1000)
        if self.player.dead:
            self.game_info[cst.PLAYER_LIVES] -= 1
            self.reset_part_game_info()
        if self.game_info[cst.PLAYER_LIVES] == 0:
            self.next = cst.STATE_GAME_OVER
        else:
            self.next = cst.STATE_YOU_DIE

    def setup_brick_and_box(self):
        '''
        设置砖块和宝箱
        :return:
        '''
        self.brick_group = pg.sprite.Group()    # 游戏中的砖块
        self.box_group = pg.sprite.Group()    # 游戏中的宝箱
        self.coin_group = pg.sprite.Group()    # 得到的金币
        self.powerup_group = pg.sprite.Group()    # 得到的加强道具

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:
                    if 'brick_num' in brick_data:
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None, self.game_info, self))
                elif brick_type == 1:
                    self.box_group.add(brick.Brick(x, y, brick_type, self.coin_group, self.game_info, self))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group, self.game_info, self))

        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group, self.game_info, self))
                else:
                    self.box_group.add(box.Box(x, y, box_type, self.powerup_group, self.game_info, self))

    def setup_enemies(self):
        '''
        设定敌人
        :return: 无
        '''
        self.shell_group = pg.sprite.Group()
        self.dead_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.enemy_group_dict = {}
        for enemy_group_data in self.map_data['enemy']:
            group = pg.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group

    def check_checkpoints(self):
        '''
        玩家到达指定地点敌人才触发
        :return: 无
        '''
        checkpoint = pg.sprite.spritecollideany(self.player, self.checkpoint_group)
        if checkpoint:
            if checkpoint.checkpoint_type == 0:
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            elif checkpoint.checkpoint_type == 2:
                self.flag_group.add(stuff.CastleFlag(8745, 322))
                self.next = cst.STATE_YOU_WIN
            elif checkpoint.checkpoint_type == 1:
                self.update_score(2000, self.flag)
                self.flag.state = 'slide_down'
            checkpoint.kill()

    def is_timeout(self):
        '''
        判断当前关卡时间是否耗尽
        :return:
        '''
        self.game_info[cst.REMAINING_TIME] = int((self.duration - (pg.time.get_ticks() - self.timer)) / 1000)
        if self.timer == 0:
            self.timer = pg.time.get_ticks()
        elif pg.time.get_ticks() - self.timer > self.duration:
            self.game_info[cst.REMAINING_TIME] = int(cst.TIME_OUT_DURATION / 1000)
            self.finished = True
            self.timer = 0
            if self.game_info[cst.EASY_OR_HARD] == cst.EASY_GAME:
                self.game_info[cst.PLAYER_LIVES] -= 1
                self.reset_part_game_info()
                if self.game_info[cst.PLAYER_LIVES] == 0:
                    self.next = cst.STATE_GAME_OVER
                else:
                    self.next = cst.STATE_TIME_OUT
            else:
                self.next = cst.STATE_GAME_OVER

    def setup_checkpoints(self):
        '''
        设定检查点
        :return: 无
        '''
        self.checkpoint_group = pg.sprite.Group()           # 把检查点加到精灵组中
        for item in self.map_data['checkpoint']:         # 下面就是获取一些检查点的基本信息
            x, y, w, h = item['x'], item['y'], item['width'], item['height']
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')       # 避免keyerror
            # 把这些checkpoint加到精灵组里
            self.checkpoint_group.add(stuff.Checkpoint(x, y, w, h, checkpoint_type, enemy_groupid))

    def setup_castle_flag(self):
        '''
        设定通关旗帜
        :return: 无
        '''
        self.flag_group = pg.sprite.Group()  # 通关旗帜

    def setup_flagpole(self):
        '''
        旗帜（包括旗杆，旗杆顶部，旗帜）
        :return:
        '''
        self.flagpole_group = pg.sprite.Group()
        if cst.FLAGPOLE in self.map_data:
            for data in self.map_data[cst.FLAGPOLE]:
                if data['type'] == cst.FLAGPOLE_FLAG:
                    sprite = stuff.Flag(data['x'], data['y'])
                    self.flag = sprite
                elif data['type'] == cst.FLAGPOLE_POLE:
                    sprite = stuff.Pole(data['x'], data['y'])
                else:
                    sprite = stuff.PoleTop(data['x'], data['y'])
                self.flagpole_group.add(sprite)

    def reset_part_game_info(self):
        '''
        每次死亡和时间耗尽再次进入关卡时得分，金币，初始状态，计时器都会重置
        :return: 无
        '''
        self.game_info.update(
            {
                cst.GAIN_SCORES: 0,
                cst.GAIN_COINS: 0,
                cst.PLAYER_STATE: cst.MARIO_START_STATE,
                cst.REMAINING_TIME: int(cst.TIME_OUT_DURATION / 1000),
            }
        )

    def update_score(self, score, sprite, coin_num=0):
        '''
        更新玩家得分（金币）
        :param score: 得分
        :param sprite: 主要用这个精灵的x，y坐标（显示得分数值用）
        :param coin_num: 获得的金币数
        :return: 无
        '''
        self.game_info[cst.GAIN_SCORES] += score
        self.game_info[cst.GAIN_COINS] += coin_num
        x = sprite.rect.x
        y = sprite.rect.y - 10
        self.score_list.append(stuff.Score(x, y, score))

    def delay_win(self):
        if self.game_win_time == 0 and self.next == cst.STATE_YOU_WIN:
            self.game_win_time = pg.time.get_ticks()
        if pg.time.get_ticks() - self.game_win_time > 2000 and self.next == cst.STATE_YOU_WIN:
            self.finished = True
