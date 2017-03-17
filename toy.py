import getpass
import os
import sys
import time
import pygame
from gtts import gTTS


class Player(object):

    def __init__(self):
        self.life1 = True
        self.life2 = True
        self.lover = None

    def player_input(self, game, player_idx):

        # Input Player ID
        clear_screen()
        hint = {'en': 'ID List:', 'zh': '玩家列表:'}
        print_hint(game, hint)
        for i_pid in range(len(game.pid_list)):
            print('%d. %s' % (i_pid + 1, game.pid_list[i_pid]))
        print('\n')
        hint = {'en': 'So, Player %d, who are you? (0 to re-input) ' % player_idx,
                'zh': '%d号玩家，报上名来！(重新输入请按0)' % player_idx}
        pid_idx = int(input(hint[game.language]))
        if pid_idx == 0 or pid_idx > len(game.pid_list):
            return self.player_input(game, player_idx)
        pid = game.pid_list[pid_idx - 1]

        # Input Roles
        clear_screen()
        hint = {'en': 'Role List:', 'zh': '角色列表:'}
        print_hint(game, hint)
        for i_role in range(len(game.role_list)):
            print('%d. %s' % (i_role + 1, game.role_list[i_role]))
        hint = {'en': '%s (Player %d), what\'s your 1st role?  (0 to re-input) ' % (pid, player_idx),
                'zh': '%s (%d号玩家)，你的第一重身份是什么(重新输入请按0)' % (pid, player_idx)}
        role1_idx = int(getpass.getpass(hint[game.language]))
        if role1_idx == 0 or role1_idx > len(game.role_list) or role1_idx == 1:
            return self.player_input(game, player_idx)
        hint = {'en': '%s (Player %d), what\'s your 2nd role?  (0 to re-input) ' % (pid, player_idx),
                'zh': '%s (%d号玩家)，你的第二重身份是什么(重新输入请按0)' % (pid, player_idx)}
        role2_idx = int(getpass.getpass(hint[game.language]))
        if role2_idx == 0 or role2_idx > len(game.role_list):
            return self.player_input(game, player_idx)

        return pid, game.role_list[role1_idx - 1], game.role_list[role2_idx - 1]

    def assign(self, pid, idx, role1, role2):
        self.pid = pid
        self.idx = idx
        self.role1 = role1
        self.role2 = role2

    def die(self):
        if self.life1:
            self.life1 = False
        elif self.life2:
            self.life2 = False
        else:
            sys.exit('Already DEAD!')   # Fix later

    def isalive(self):
        if self.life2 == False:
            return False
        else:
            return True

    def cur_role(self):
        if self.life1:
            return self.role1
        elif self.life2:
            return self.role2
        else:
            return None


class Game(object):

    def __init__(self, role_list, pid_list, n_player, language):
        self.role_list = role_list
        self.pid_list = pid_list
        self.n_player = n_player
        self.player_list = []
        self.team_good = set([])
        self.team_evil = set([])
        self.team_love = set([])
        self.cupid_idx = None
        self.alpha_idx = None
        self.kill_idx = []
        self.guard_idx = []
        self.heal_idx = []
        self.poison_idx = []
        self.vote_idx = []
        self.heal_exist = True
        self.poison_exist = True
        self.elder_protect = True
        self.hunter_activate = False
        self.elder_vote_to_death = False
        self.language = language
        self.lastword_cnt = 0

    def init_player_list(self):

        # Initialize Player IDs & Roles
        for i_player in range(self.n_player):
            _player = Player()
            pid, role1, role2 = _player.player_input(self, i_player + 1)
            _player.assign(pid, len(self.player_list) + 1, role1, role2)
            self.player_list.append(_player)

        # Initialize Teams
        for player in self.player_list:
            if player.role1 == 'Cupid' or player.role2 == 'Cupid' or \
                            player.role1 == '丘比特' or player.role2 == '丘比特':
                self.cupid_idx = player.idx
            if player.role2 == "Alpha Werewolf" or player.role2 == '大野狼':
                self.alpha_idx = player.idx
            if player.role1 == "Werewolf" or player.role2 == "Werewolf" or player.role2 == "Alpha Werewolf" or \
                player.role1 == '狼人' or player.role2 == '狼人' or player.role2 == '大野狼':
                self.team_evil.add(player.idx)
            else:
                self.team_good.add(player.idx)

    def demo_init_player_list(self):
        _pid_idx_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        _role1_idx_list = [2, 8, 3, 8, 8, 5, 6, 7, 8]
        _role2_idx_list = [8, 8, 8, 1, 4, 8, 8, 8, 2]
        for i_player in range(self.n_player):
            _player = Player()
            _player.assign(self.pid_list[_pid_idx_list[i_player] - 1], i_player + 1,
                           self.role_list[_role1_idx_list[i_player] - 1], self.role_list[_role2_idx_list[i_player] - 1])
            self.player_list.append(_player)
        for player in self.player_list:
            if player.role1 == 'Cupid' or player.role2 == 'Cupid' or \
                            player.role1 == '丘比特' or player.role2 == '丘比特':
                self.cupid_idx = player.idx
            if player.role2 == "Alpha Werewolf" or player.role2 == '大野狼':
                self.alpha_idx = player.idx
            if player.role1 == "Werewolf" or player.role2 == "Werewolf" or player.role2 == "Alpha Werewolf" or \
                player.role1 == '狼人' or player.role2 == '狼人' or player.role2 == '大野狼':
                self.team_evil.add(player.idx)
            else:
                self.team_good.add(player.idx)

    def show_player_list_all(self):
        clear_screen()
        hint = {'en': 'Player', 'zh': '玩家'}
        for i_player in range(self.n_player):
            _player = self.player_list[i_player]
            print('%s %2i  |  %15s  | %15s  | %15s' % (hint[self.language], _player.idx,
                                                       _player.pid, _player.role1, _player.role2))

    def show_player_list(self):
        clear_screen()
        hint = {'en': 'Player', 'zh': '玩家'}
        for i_player in range(self.n_player):
            _player = self.player_list[i_player]
            print('%s %2i    %15s' % (hint[self.language], _player.idx, _player.pid))

    def ispresent(self, role):
        _cur_role_list = []
        for _player in self.player_list:
            _cur_role_list.append(_player.cur_role())
        if role in _cur_role_list:
            return True
        else:
            return False

    def isdead(self, role):
        _all_role_list = []
        for _player in self.player_list:
            if _player.life1:
                _all_role_list.append(_player.role1)
                _all_role_list.append(_player.role2)
            elif _player.life2:
                _all_role_list.append(_player.role2)
            else:
                _all_role_list.append(None)
        if role in _all_role_list:
            return False
        else:
            return True

    def dielove(self, dead_idx):
        if (not self.player_list[dead_idx - 1].life1) and \
            (not self.player_list[dead_idx - 1].lover == None) and \
                (self.player_list[dead_idx - 1].lover.isalive()):
            if self.player_list[dead_idx - 1].lover.life1:
                dead_man_tuple = (self.player_list[dead_idx - 1].lover.idx, 2)
                return dead_man_tuple
            else:
                dead_man_tuple = (self.player_list[dead_idx - 1].lover.idx, 1)
                return dead_man_tuple
        else:
            return None

    def night(self, iday):
        clear_screen()
        hint = {'en': 'Everybody, close your eyes!', 'zh': '天黑请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 3)

        # Action Evil
        if not len(self.team_evil) == 0:
            clear_screen()
            hint = {'en': 'Werewolves, wake up!', 'zh': '狼人，醒醒!'}
            print_hint(self, hint)
            speak_hint(self, hint, 2)
            kill_tn = self.action_evil()
        else:
            kill_tn = 0
        self.kill_idx.append(kill_tn)

        # Action Guard
        clear_screen()
        if ((not self.isdead('Guard')) or (not self.isdead('守卫'))) and (not self.elder_vote_to_death):
            hint = {'en': 'Guard, open your eyes!', 'zh': '守卫，请睁眼!'}
            print_hint(self, hint)
            speak_hint(self, hint, 2)
            guard_tn = self.action_guard()
        else:
            guard_tn = 0
        self.guard_idx.append(guard_tn)

        # Action Witch
        clear_screen()
        if ((not self.isdead('Witch')) or (not self.isdead('女巫'))) and (not self.elder_vote_to_death):
            hint = {'en': 'Witch, open your eyes!', 'zh': '女巫，请睁眼!'}
            print_hint(self, hint)
            speak_hint(self, hint, 2)
            heal_tn, poison_tn = self.action_witch()
        else:
            heal_tn, poison_tn = 0, 0
        self.heal_idx.append(heal_tn)
        self.poison_idx.append(poison_tn)

        # Generate the death list tonight
        dead_tn = []
        lastword_tn = []
        if not poison_tn == 0:
            dead_tn.append((poison_tn, 1))
        if (not kill_tn == 0) and (not kill_tn == guard_tn) and (not kill_tn == heal_tn):
            if self.player_list[kill_tn - 1].cur_role() in ['Elder', '长老'] and self.elder_protect:
                self.elder_protect = False
            else:
                dead_tn.append((kill_tn, 1))
                lastword_tn.append(kill_tn)
        dead_tn = reduce_deadlist(dead_tn)
        dead_tn = self.dl_check_love(dead_tn)

        # Announce the death list
        clear_screen()
        hint = {'en': 'Everybody, open your eyes!', 'zh': '天亮请睁眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 2)
        press_enter(self)

        clear_screen()
        if len(dead_tn) == 0:
            hint = {'en': 'No Death Last Night!', 'zh': '昨晚是平安夜'}
            print_hint(self, hint)
        else:
            hint = {'en': 'Last Night\'s Death List:', 'zh': '昨晚死掉的人有:'}
            print_hint(self, hint)
            for dead_rec in dead_tn:
                if dead_rec[1] == 1:
                    hint = {'en': 'Player %d (%s) Lost 1 Life' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失一条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                    self.player_list[dead_rec[0] - 1].die()
                else:
                    hint = {'en': 'Player %d (%s) Lost 2 Lives' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失两条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                    self.player_list[dead_rec[0] - 1].die()
                    self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                    self.player_list[dead_rec[0] - 1].die()
            if (len(lastword_tn) == 0) or (self.lastword_cnt >= 3):
                hint = {'en': 'No player is eligible to leave last word.',
                        'zh': '没有玩家可以留下遗言.'}
                print_hint(self, hint)
            else:
                self.lastword_cnt = self.lastword_cnt + 1
                hint = {'en': 'Player %d (%s), please leave your last word.'
                              % (lastword_tn[0], self.player_list[lastword_tn[0] - 1].pid),
                        'zh': '请%d号玩家(%s)留遗言.'
                              % (lastword_tn[0], self.player_list[lastword_tn[0] - 1].pid)}
                print_hint(self, hint)
        press_enter(self)
        if self.hunter_activate and (not self.elder_vote_to_death):
            hint = {'en': 'Hunter! Shoot! Now!', 'zh': '猎人请开枪！'}
            print_hint(self, hint)
            shoot_idx = self.action_hunter()
            dead_shoot = [(shoot_idx, 1)]
            dead_shoot = self.dl_check_love(dead_shoot)
            dead_shoot = reduce_deadlist(dead_shoot)
            hint = {'en': 'Death List after shooting:',
                    'zh': '猎人开枪之后死掉的人有:'}
            print_hint(self, hint)
            for dead_rec in dead_shoot:
                if dead_rec[1] == 1:
                    hint = {'en': 'Player %d (%s) Lost 1 Life' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失一条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.player_list[dead_rec[0] - 1].die()
                else:
                    hint = {'en': 'Player %d (%s) Lost 2 Lives' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失两条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.player_list[dead_rec[0] - 1].die()
                    self.player_list[dead_rec[0] - 1].die()
            self.hunter_activate = False
            press_enter(self)
        press_enter(self)

    def first_night(self):

        clear_screen()
        hint = {'en': 'Everybody, close your eyes!', 'zh': '天黑请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 3)

        # Action Cupid
        clear_screen()
        hint = {'en': 'Cupid, open your eyes!', 'zh': '丘比特，请睁眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 2)
        self.action_cupid()

        # Action Evil
        clear_screen()
        hint = {'en': 'Werewolves, wake up!', 'zh': '狼人，醒醒!'}
        print_hint(self, hint)
        speak_hint(self, hint, 2)
        kill_tn = self.action_evil()
        self.kill_idx.append(kill_tn)

        # Action Guard
        clear_screen()
        hint = {'en': 'Guard, open your eyes!', 'zh': '守卫，请睁眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 2)
        guard_tn = self.action_guard()
        self.guard_idx.append(guard_tn)

        # Action Witch
        clear_screen()
        hint = {'en': 'Witch, open your eyes!', 'zh': '女巫，请睁眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 2)
        heal_tn, poison_tn = self.action_witch()
        self.heal_idx.append(heal_tn)
        self.poison_idx.append(poison_tn)

        # Generate the death list tonight
        dead_tn = []
        lastword_tn = []
        if not poison_tn == 0:
            dead_tn.append((poison_tn, 1))
        if (not kill_tn == 0) and (not kill_tn == guard_tn) and (not kill_tn == heal_tn):
            if self.player_list[kill_tn - 1].cur_role() in ['Elder', '长老'] and self.elder_protect:
                self.elder_protect = False
            else:
                dead_tn.append((kill_tn, 1))
                lastword_tn.append(kill_tn)
        dead_tn = reduce_deadlist(dead_tn)
        dead_tn = self.dl_check_love(dead_tn)

        # Announce the death list
        clear_screen()
        hint = {'en': 'Everybody, open your eyes!', 'zh': '天亮请睁眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 2)
        hint = {'en': 'Please Elect the Sheriff!', 'zh': '竞选警长!'}
        print_hint(self, hint)
        press_enter(self)

        clear_screen()
        if len(dead_tn) == 0:
            hint = {'en': 'No Death Last Night!', 'zh': '昨晚是平安夜'}
            print_hint(self, hint)
        else:
            hint = {'en': 'Last Night\'s Death List:', 'zh': '昨晚死掉的人有:'}
            print_hint(self, hint)
            for dead_rec in dead_tn:
                if dead_rec[1] == 1:
                    hint = {'en': 'Player %d (%s) Lost 1 Life' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失一条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                    self.player_list[dead_rec[0] - 1].die()
                else:
                    hint = {'en': 'Player %d (%s) Lost 2 Lives' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失两条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                    self.player_list[dead_rec[0] - 1].die()
                    self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                    self.player_list[dead_rec[0] - 1].die()
            if len(lastword_tn) == 0:
                hint = {'en': 'No player is eligible to leave last word.',
                        'zh': '没有玩家可以留下遗言.'}
                print_hint(self, hint)
            else:
                hint = {'en': 'Player %d (%s), please leave your last word.'
                              % (lastword_tn[0], self.player_list[lastword_tn[0] - 1].pid),
                        'zh': '请%d号玩家(%s)留遗言.'
                                % (lastword_tn[0], self.player_list[lastword_tn[0] - 1].pid)}
                print_hint(self, hint)
        press_enter(self)
        if self.hunter_activate and (not self.elder_vote_to_death):
            hint = {'en': 'Hunter! Shoot! Now!', 'zh': '猎人请开枪！'}
            print_hint(self, hint)
            shoot_idx = self.action_hunter()
            dead_shoot = [(shoot_idx, 1)]
            dead_shoot = self.dl_check_love(dead_shoot)
            dead_shoot = reduce_deadlist(dead_shoot)
            hint = {'en': 'Death List after shooting:',
                    'zh': '猎人开枪之后死掉的人有:'}
            print_hint(self, hint)
            for dead_rec in dead_shoot:
                if dead_rec[1] == 1:
                    hint = {'en': 'Player %d (%s) Lost 1 Life' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失一条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.player_list[dead_rec[0] - 1].die()
                else:
                    hint = {'en': 'Player %d (%s) Lost 2 Lives' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失两条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.player_list[dead_rec[0] - 1].die()
                    self.player_list[dead_rec[0] - 1].die()
            self.hunter_activate = False
            press_enter(self)
        press_enter(self)

    def day(self, iday):
        clear_screen()
        self.show_player_list()
        hint = {'en': 'Please vote a player to death: ',
                'zh': '请选择投票杀死的玩家: '}
        vote_td = int(input(hint[self.language]))
        hint = {'en': 'Are you sure? (0 - Redo; 1 - Confirm) ',
                'zh': '你们确定么？(确认请按1，重新输入请按0) '}
        i_sure = input(hint[self.language])
        if not i_sure == '1':
            return self.day(iday)
        self.vote_idx.append(vote_td)
        if self.player_list[vote_td - 1].cur_role() in ['Elder' or '长老']:
            self.elder_vote_to_death = True
            hint = {'en': 'Elder is voted to death. Now, all the roles lost their skills.',
                    'zh': '长老被投死。所有人失去技能.'}
            print_hint(self, hint)
        dead_td = [(vote_td, 1)]
        dead_td = self.dl_check_love(dead_td)
        dead_td = reduce_deadlist(dead_td)

        hint = {'en': 'Day %d. Today\'s Death List:' % iday,
                'zh': '第%d天. 今天死掉的人有:' % iday}
        print_hint(self, hint)
        for dead_rec in dead_td:
            if dead_rec[1] == 1:
                hint = {'en': 'Player %d (%s) Lost 1 Life' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                        'zh': '%d号玩家(%s)丧失一条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                print_hint(self, hint)
                self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                self.player_list[dead_rec[0] - 1].die()
            else:
                hint = {'en': 'Player %d (%s) Lost 2 Lives' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                        'zh': '%d号玩家(%s)丧失两条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                print_hint(self, hint)
                self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                self.player_list[dead_rec[0] - 1].die()
                self.check_hunter_stat(self.player_list[dead_rec[0] - 1])
                self.player_list[dead_rec[0] - 1].die()
        press_enter(self)
        if self.hunter_activate and (not self.elder_vote_to_death):
            hint = {'en': 'Hunter! Shoot! Now!', 'zh': '猎人请开枪！'}
            print_hint(self, hint)
            shoot_idx = self.action_hunter()
            dead_shoot = [(shoot_idx, 1)]
            dead_shoot = self.dl_check_love(dead_shoot)
            dead_shoot = reduce_deadlist(dead_shoot)
            hint = {'en': 'Death List after shooting:',
                    'zh': '猎人开枪之后死掉的人有:'}
            print_hint(self, hint)
            for dead_rec in dead_shoot:
                if dead_rec[1] == 1:
                    hint = {'en': 'Player %d (%s) Lost 1 Life' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失一条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.player_list[dead_rec[0] - 1].die()
                else:
                    hint = {'en': 'Player %d (%s) Lost 2 Lives' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid),
                            'zh': '%d号玩家(%s)丧失两条生命' % (dead_rec[0], self.player_list[dead_rec[0] - 1].pid)}
                    print_hint(self, hint)
                    self.player_list[dead_rec[0] - 1].die()
                    self.player_list[dead_rec[0] - 1].die()
            self.hunter_activate = False
            press_enter(self)
        press_enter(self)

    def isover(self):
        team_good_tmp = tuple(self.team_good)
        team_evil_tmp = tuple(self.team_evil)
        team_love_tmp = tuple(self.team_love)
        for idx_good in team_good_tmp:
            if not self.player_list[idx_good - 1].isalive():
                self.team_good.remove(idx_good)
        for idx_evil in team_evil_tmp:
            if not self.player_list[idx_evil - 1].isalive():
                self.team_evil.remove(idx_evil)
        for idx_love in team_love_tmp:
            if not self.player_list[idx_love - 1].isalive():
                self.team_love.remove(idx_love)
        if (not len(self.team_good) == 0) and (len(self.team_evil) == 0) and (len(self.team_love) == 0):
            hint = {'en': 'The Good WIN!!!', 'zh': '人民群众取得了胜利!'}
            print_hint(self, hint)
            press_enter(self)
            return True
        elif (len(self.team_good) == 0) and (not len(self.team_evil) == 0) and (len(self.team_love) == 0):
            hint = {'en': 'The Evil WIN!!!', 'zh': '狼人取得了胜利!'}
            print_hint(self, hint)
            press_enter(self)
            return True
        elif (len(self.team_good) == 0) and (len(self.team_evil) == 0) and (len(self.team_love) == 0):
            hint = {'en': 'The Lovers WIN!!!', 'zh': '情侣取得了胜利!'}
            print_hint(self, hint)
            press_enter(self)
            return True
        else:
            return False

    def action_cupid(self):
        press_enter(self)
        clear_screen()
        self.show_player_list()
        print('')
        hint = {'en': 'Please assign Lover No. 1: ',
                'zh': '请输入情侣之一: '}
        lover1_idx = int(input(hint[self.language]))
        hint = {'en': 'Please assign Lover No. 2: ',
                'zh': '请输入情侣之二: '}
        lover2_idx = int(input(hint[self.language]))
        lover1 = self.player_list[lover1_idx - 1]
        lover2 = self.player_list[lover2_idx - 1]
        hint = {'en': 'So, the lovers you just assigned are Player %d (%s) and Player %d (%s).'
                      % (lover1_idx, lover1.pid, lover2_idx, lover2.pid),
                'zh': '所以，你所指定的情侣为%d号玩家(%s)与%d号玩家(%s).'
                      % (lover1_idx, lover1.pid, lover2_idx, lover2.pid)}
        print_hint(self, hint)
        hint = {'en': 'Are you sure? (0 - Re-assign; 1 - Confirm) ',
                'zh': '你确定吗？(重新输入请按0， 确认请按1)'}
        i_sure = input(hint[self.language])
        if not i_sure == '1':
            return self.action_cupid()

        self.player_list[lover1_idx - 1].lover = self.player_list[lover2_idx - 1]
        self.player_list[lover2_idx - 1].lover = self.player_list[lover1_idx - 1]
        if (lover1_idx in self.team_good) and (lover2_idx in self.team_good) and (self.cupid_idx in self.team_good):
            pass
        elif (lover1_idx in self.team_evil) and (lover2_idx in self.team_evil) and (self.cupid_idx in self.team_evil):
            pass
        else:
            rm_list_tmp = [lover1_idx, lover2_idx, self.cupid_idx]
            for idx_tmp in rm_list_tmp:
                if idx_tmp in self.team_good:
                    self.team_good.remove(idx_tmp)
                if idx_tmp in self.team_evil:
                    self.team_evil.remove(idx_tmp)
            self.team_love.add(lover1_idx)
            self.team_love.add(lover2_idx)

        clear_screen()
        hint = {'en': 'Everyone, stick out your hand!',
                'zh': '请大家把手伸出！'}
        print_hint(self, hint)
        speak_hint(self, hint, 3)
        hint = {'en': 'Cupid, please poke the lovers!',
                'zh': '丘比特，请轻戳你指定的情侣!'}
        print_hint(self, hint)
        speak_hint(self, hint, 3)
        press_enter(self)

        clear_screen()
        hint = {'en': 'Cupid, close your eyes!',
                'zh': '丘比特，请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 6)
        hint = {'en': 'Now, the lovers look into each others\' eyes!',
                'zh': '情侣请睁眼认识一下对方!'}
        print_hint(self, hint)
        speak_hint(self, hint, 3)
        press_enter(self)
        hint = {'en': 'Lovers, please close your eyes!',
                'zh': '情侣，请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 6)

    def action_evil_old(self):
        press_enter(self)
        self.show_player_list()
        print('')
        hint = {'en': 'Please select a player you want to KILL tonight! (0 - Cannot Decide)',
                'zh': '请选择今天晚上的作案目标! (无法决定请按0)'}
        kill_idx = int(input(hint[self.language]))
        hint = {'en': 'Are you sure? (0 - Redo; 1 - Confirm) ',
                'zh': '你确定么？(确认请按1，重新输入请按0) '}
        i_sure = input(hint[self.language])
        if not i_sure == '1':
            return self.action_evil()
        clear_screen()
        hint = {'en': 'Werewolves, please close your eyes!',
                'zh': '狼人，请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 6)
        return kill_idx

    def action_evil(self):
        if self.ispresent('Werewolf') or self.ispresent('狼人') or (self.player_list[self.alpha_idx - 1].isalive()):
            press_enter(self)
            self.show_player_list()
            print('')
            hint = {'en': 'Please select a player you want to KILL tonight! (0 - Cannot Decide) ',
                    'zh': '请选择今天晚上的作案目标! (无法决定请按0) '}
            kill_idx = int(input(hint[self.language]))
            hint = {'en': 'Are you sure? (0 - Redo; 1 - Confirm) ',
                    'zh': '你确定么？(确认请按1，重新输入请按0) '}
            i_sure = input(hint[self.language])
            if not i_sure == '1':
                return self.action_evil()
        else:
            time.sleep(10)
            kill_idx = 0
        clear_screen()
        hint = {'en': 'Werewolves, please close your eyes!',
                'zh': '狼人，请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 6)
        return kill_idx

    def action_guard(self):
        if self.ispresent('Guard') or self.ispresent('守卫'):
            press_enter(self)
            self.show_player_list()
            if len(self.guard_idx) > 0:
                if not self.guard_idx[-1] == 0:
                    last_guard = self.player_list[self.guard_idx[-1] - 1]
                    hint = {'en': 'The player you guard last night is Player %d (%s)' % (last_guard.idx, last_guard.pid),
                            'zh': '你昨晚守护的人是%d号玩家(%s)' % (last_guard.idx, last_guard.pid)}
                    print_hint(self, hint)
            hint = {'en': 'Please select a player you want to GUARD tonight! ',
                    'zh': '请选择一个你今晚要守护的人! '}
            guard_idx = int(input(hint[self.language]))
            hint = {'en': 'Are you sure? (0 - Redo; 1 - Confirm) ',
                    'zh': '你确定么？(确认请按1，重新输入请按0) '}
            i_sure = input(hint[self.language])
            if not i_sure == '1':
                return self.action_guard()
            if len(self.guard_idx) > 0:
                if last_guard.idx == guard_idx:
                    hint = {'en': 'You cannot guard the same player for two nights in a row! Please reselect.',
                            'zh': '你不能连续两夜守护同一位玩家！请重新选择.'}
                    print_hint(self, hint)
                    return self.action_guard()
        else:
            time.sleep(10)
            guard_idx = 0
        clear_screen()
        hint = {'en': 'Guard, please close your eyes!',
                'zh': '守卫，请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 6)
        return guard_idx

    def action_witch(self):
        if self.ispresent('Witch') or self.ispresent('女巫'):
            press_enter(self)
            self.show_player_list()
            if self.heal_exist:
                hint = {'en': 'Tonight, the player killed by the evil is Player %d (%s).'
                              % (self.kill_idx[-1], self.player_list[self.kill_idx[-1] - 1].pid),
                        'zh': '今晚，被狼人杀死的是%d号玩家(%s).'
                              % (self.kill_idx[-1], self.player_list[self.kill_idx[-1] - 1].pid)}
                print_hint(self, hint)
                hint = {'en': 'Are you gonna HEAL him/her? (0 - Nope; 1 - Yep!) ',
                        'zh': '你要对TA用解药吗？(不用请按0，用请按1)'}
                heal_tn = int(input(hint[self.language])) * self.kill_idx[-1]
                if not heal_tn == 0:
                    self.heal_exist = False
            else:
                hint = {'en': 'You DO NOT have the antidote.',
                        'zh': '你没有解药了.'}
                print_hint(self, hint)
                heal_tn = 0
                press_enter(self)
            if self.poison_exist:
                hint = {'en': 'Which player are you gonna POISON tonight? (0 - None) ',
                        'zh': '你打算对哪位玩家使用毒药? (不用请按0) '}
                poison_tn = int(input(hint[self.language]))
                if not poison_tn == 0:
                    self.poison_exist = False
            else:
                hint = {'en': 'You DO NOT have the poison.',
                        'zh': '你没有毒药了.'}
                print_hint(self, hint)
                poison_tn = 0
                press_enter(self)
            hint = {'en': 'Are you sure? (0 - Redo; 1 - Confirm) ',
                    'zh': '你确定么？(确认请按1，重新输入请按0) '}
            i_sure = input(hint[self.language])
            if not i_sure == '1':
                return self.action_witch()
        else:
            time.sleep(10)
            heal_tn = 0
            poison_tn = 0
        clear_screen()
        hint = {'en': 'Witch, please close your eyes!',
                'zh': '女巫，请闭眼!'}
        print_hint(self, hint)
        speak_hint(self, hint, 6)
        return heal_tn, poison_tn

    def action_hunter(self):
        self.show_player_list()
        print('')
        hint = {'en': 'Please select a player you want to shoot! ',
                'zh': '请选择你要击毙的玩家! '}
        shoot_idx = int(input(hint[self.language]))
        hint = {'en': 'Are you sure? (0 - Redo; 1 - Confirm) ',
                'zh': '你确定么？(确认请按1，重新输入请按0) '}
        i_sure = input(hint[self.language])
        if not i_sure == '1':
            return self.action_hunter()
        return shoot_idx

    def dl_check_love(self, dead_tn):
        dead_tn_tmp = dead_tn
        for dead_man in dead_tn_tmp:
            dielove_tmp = self.dielove(dead_man[0])
            if dielove_tmp:
                dead_tn.append(dielove_tmp)
        dead_tn = reduce_deadlist(dead_tn)
        return dead_tn

    def check_hunter_stat(self, player_to_death):
        if player_to_death.cur_role() in ['Hunter', '猎人']:
            self.hunter_activate = True

    def end(self):
        press_enter(self)
        self.show_history()
        return

    def show_history(self):
        self.show_player_list_all()
        hint = {'en': 'Cupid: Player %d %s' % (self.cupid_idx, self.player_list[self.cupid_idx - 1].pid),
                'zh': '丘比特: %d号玩家%s' % (self.cupid_idx, self.player_list[self.cupid_idx - 1].pid)}
        print_hint(self, hint)

        lover_idx_list = []
        lover_pid_list = []
        for player in self.player_list:
            if not player.lover == None:
                lover_idx_list.append(player.idx)
                lover_pid_list.append(player.pid)
                lover_idx_list.append(player.lover.idx)
                lover_pid_list.append(player.lover.pid)
                break
        hint = {'en': 'Lovers: Player %d (%s) and Player %d (%s)'
                      % (lover_idx_list[0], lover_pid_list[0], lover_idx_list[1], lover_pid_list[1]),
                'zh': '情侣：%d号玩家(%s) 与 %d号玩家(%s)'
                      % (lover_idx_list[0], lover_pid_list[0], lover_idx_list[1], lover_pid_list[1])}
        print_hint(self, hint)

        hint = {'en': 'Werewolf kill history:',
                'zh': '狼人杀人历史:'}
        print_hint(self, hint)
        his = ''
        for i in range(len(self.kill_idx)):
            his = his + '%5d' % self.kill_idx[i]
        print(his)

        hint = {'en': 'Heal history:',
                'zh': '解药历史:'}
        print_hint(self, hint)
        his = ''
        for i in range(len(self.heal_idx)):
            his = his + '%5d' % self.heal_idx[i]
        print(his)

        hint = {'en': 'Poison history:',
                'zh': '毒药历史:'}
        print_hint(self, hint)
        his = ''
        for i in range(len(self.poison_idx)):
            his = his + '%5d' % self.poison_idx[i]
        print(his)

        hint = {'en': 'Guard history:',
                'zh': '守卫历史:'}
        print_hint(self, hint)
        his = ''
        for i in range(len(self.guard_idx)):
            his = his + '%5d' % self.guard_idx[i]
        print(his)

        hint = {'en': 'Vote history:',
                'zh': '投票历史:'}
        print_hint(self, hint)
        his = ''
        for i in range(len(self.vote_idx)):
            his = his + '%5d' % self.vote_idx[i]
        print(his)
        return


def press_enter(game):
    hint = {'en': 'Press Enter to Continue.', 'zh': '请按回车键继续'}
    h = input(hint[game.language])
    if h == 'h':
        game.show_history()
        press_enter(game)
    return


def clear_screen():
    os.system('clear')


def print_hint(game, hint):
    print(hint[game.language])


def speak_hint(game, hint, t_sleep):
    tts = gTTS(text=hint[game.language], lang=game.language)
    tts.save("temp.mp3")
    pygame.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    time.sleep(t_sleep)


def reduce_deadlist(dead_tn):
    dead_tn = sorted(dead_tn, key=lambda x: x[0])
    new_dead_tn = []
    idx_list = sorted(list(set(x[0] for x in dead_tn)))
    for idx in idx_list:
        lost_life = []
        for dead_record in dead_tn:
            if dead_record[0] == idx:
                lost_life.append(dead_record[1])
        new_dead_tn.append((idx, max(lost_life)))
    dead_tn = new_dead_tn
    return dead_tn


def main():

    role_list_all = {'en':['Alpha Werewolf', 'Werewolf', 'Cupid', 'Guard', 'Witch', 'Hunter', 'Elder', 'Villager'],
                     'zh': ['大野狼', '狼人', '丘比特', '守卫', '女巫', '猎人', '长老', '普通村民']}
    pid_list_all = {'en': ['Tuojie', 'Chaoge', 'Xiaoyang', 'Feifei', 'Jiajia', 'Haoge', 'Zhao Hangqi',
                           'Little Xiannv', 'Jeremy', 'Hantang', 'Tony Leung'],
                    'zh': ['拓姐', '超哥', '杨潇', '非非', '汪佳佳', '浩哥', '赵航琪',
                           '小仙女', '杰雷米', '汉唐', '梁朝伟']}
    n_player = 9
    language = 'zh'

    # Initialization
    game = Game(role_list_all[language], pid_list_all[language], n_player, language)
    welcome_hint = {'en': 'Welcome to the Werewolf Kill Moderator Liberator! Please Input Player Info!',
                    'zh': '欢迎来到狼人杀法官解放者！请录入玩家信息！'}
    clear_screen()
    print_hint(game, welcome_hint)
    speak_hint(game, welcome_hint, 5)
    # game.init_player_list()
    game.demo_init_player_list()
    # game.show_player_list()

    # First Night
    press_enter(game)
    iday = 1
    game.first_night()
    if game.isover():
        game.end()
        return
    press_enter(game)

    # Days go by
    while True:
        iday+= 1
        game.day(iday)
        if game.isover():
            game.end()
            return
        press_enter(game)
        game.night(iday)
        if game.isover():
            game.end()
            return
        press_enter(game)

main()