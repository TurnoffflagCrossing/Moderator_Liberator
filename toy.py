import getpass
import os
import sys
import time


class Player(object):

    def __init__(self):
        self.life1 = True
        self.life2 = True
        self.lover = None

    def player_input(self, pid_list, role_list, player_idx):
        n_pid = len(pid_list)
        n_role = len(role_list)
        clear_screen()
        print('ID List:')
        for i_pid in range(n_pid):
            print('%d. %s' % (i_pid + 1, pid_list[i_pid]))
        pid_idx = int(input('So, Player %d, who are you? (0 to re-input) ' %player_idx))
        if pid_idx == 0 or pid_idx > len(pid_list):
            return self.player_input(pid_list, role_list, player_idx)
        pid = pid_list[pid_idx - 1]
        clear_screen()
        print('Role List:')
        for i_role in range(n_role):
            print('%d. %s' % (i_role + 1, role_list[i_role]))
        role1_idx = int(getpass.getpass('%s (Player %d), what\'s your 1st role?  (0 to re-input) ' % (pid, player_idx)))
        if role1_idx == 0 or role1_idx > len(role_list):
            return self.player_input(pid_list, role_list, player_idx)
        role2_idx = int(getpass.getpass('%s (Player %d), what\'s your 2nd role?  (0 to re-input) ' % (pid, player_idx)))
        if role2_idx == 0 or role2_idx > len(role_list):
            return self.player_input(pid_list, role_list, player_idx)
        return pid, role_list[role1_idx - 1], role_list[role2_idx - 1]

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
            sys.exit('Already DEAD!')

    def isalive(self):
        if self.life2 == False:
            return False
        else:
            return True


class Game(object):

    def __init__(self, role_list, pid_list, n_player):
        self.role_list = role_list
        self.pid_list = pid_list
        self.n_player = n_player
        self.player_list = []
        self.team_good = set([])
        self.team_evil = set([])
        self.team_love = set([])
        self.cupid_idx = None
        self.kill_idx = []
        self.guard_idx = []
        self.heal_idx = []
        self.poison_idx = []

    def init_player_list(self):
        for i_player in range(self.n_player):
            _player = Player()
            pid, role1, role2 = _player.player_input(self.pid_list, self.role_list, i_player + 1)
            _player.assign(pid, len(self.player_list) + 1, role1, role2)
            self.player_list.append(_player)
        for player in self.player_list:
            if player.role1 == "Cupid" or player.role2 == "Cupid":
                self.cupid_idx = player.idx
            if player.role1 == "Werewolf" or player.role2 == "Werewolf" or player.role2 == "Alpha Werewolf":
                self.team_evil.add(player.idx)
            else:
                self.team_good.add(player.idx)

    def demo_init_player_list(self):
        _pid_idx_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        _role1_idx_list = [2, 8, 3, 8, 4, 5, 6, 7, 8]
        _role2_idx_list = [8, 8, 8, 1, 8, 8, 8, 8, 2]
        for i_player in range(self.n_player):
            _player = Player()
            _player.assign(self.pid_list[_pid_idx_list[i_player] - 1], i_player + 1,
                           self.role_list[_role1_idx_list[i_player] - 1], self.role_list[_role2_idx_list[i_player] - 1])
            self.player_list.append(_player)
        for player in self.player_list:
            if player.role1 == "Cupid" or player.role2 == "Cupid":
                self.cupid_idx = player.idx
            if player.role1 == "Werewolf" or player.role2 == "Werewolf" or player.role2 == "Alpha Werewolf":
                self.team_evil.add(player.idx)
            else:
                self.team_good.add(player.idx)

    def show_player_list_all(self):
        clear_screen()
        for i_player in range(self.n_player):
            _player = self.player_list[i_player]
            print('Player %2i  |  %15s  | %15s  | %15s' % (_player.idx, _player.pid, _player.role1, _player.role2))
        press_enter()

    def show_player_list(self):
        clear_screen()
        for i_player in range(self.n_player):
            _player = self.player_list[i_player]
            print('Player %2i    %15s' % (_player.idx, _player.pid))

    def first_night(self):

        clear_screen()
        print('Everybody, close your eyes!')
        press_enter()

        clear_screen()
        print('Cupid, open your eyes')
        self.action_cupid()

        clear_screen()
        print('Werewolves, open your eyes!')
        kill_tn = self.action_evil()
        self.kill_idx.append(kill_tn)

        clear_screen()
        print('Guard, open your eyes!')
        guard_tn = self.action_guard()
        self.guard_idx.append(guard_tn)

        clear_screen()
        print('Witch, open your eyes!')
        heal_tn, poison_tn = self.action_witch()
        self.heal_idx.append(heal_tn)
        self.poison_idx.append(poison_tn)

        # Generate the death list tonight
        dead_tn = []
        lastword_tn = set([])
        if not poison_tn == 0:
            dead_tn.append([poison_tn, 1])
        if (not kill_tn == 0) and (not kill_tn == guard_tn) and (not kill_tn == heal_tn):
            dead_tn.append([kill_tn, 1])
            lastword_tn.add(kill_tn)

        for dead_idx in dead_tn:
            self.player_list[dead_idx[0] - 1].die()
            if (not self.player_list[dead_idx[0] - 1].isalive()) and \
                    (not self.player_list[dead_idx[0] - 1].lover == None) \
                    and (self.player_list[dead_idx[0] - 1].lover.isalive()):
                if self.player_list[dead_idx[0] - 1].lover.life1:
                    self.player_list[dead_idx[0] - 1].lover.die()
                    self.player_list[dead_idx[0] - 1].lover.die()
                    dead_tn.append([self.player_list[dead_idx[0] - 1].lover.idx, 2])
                else:
                    self.player_list[dead_idx[0] - 1].lover.die()
                    dead_tn.append([self.player_list[dead_idx[0] - 1].lover.idx, 1])

        # Announce the death list
        clear_screen()
        print('Everybody, open your eyes!')
        press_enter()
        clear_screen()
        dead_tn = sorted(dead_tn, key = lambda x: x[0])
        if len(dead_tn) == 0:
            print('No Death Tonight!')
        else:
            print('Tonight\'s Death List:')
            for dead in dead_tn:
                if dead[1] == 1:
                    print('Player %d (%s) Lost 1 Life' % (dead[0], self.player_list[dead[0] - 1].pid))
                elif dead[1] == 2:
                    print('Player %d (%s) Lost 2 Lives' % (dead[0], self.player_list[dead[0] - 1].pid))

    def isover(self):
        for idx_good in self.team_good:
            if not self.player_list[idx_good - 1].isalive():
                self.team_good.remove(idx_good)
        for idx_evil in self.team_evil:
            if not self.player_list[idx_evil - 1].isalive():
                self.team_evil.remove(idx_evil)
        for idx_love in self.team_love:
            if not self.player_list[idx_love - 1].isalive():
                self.team_love.remove(idx_love)
        if (not len(self.team_good) == 0) and (len(self.team_evil) == 0) and (len(self.team_love) == 0):
            print('The Good WIN!!!')
            press_enter()
            sys.exit()
        elif (len(self.team_good) == 0) and (not len(self.team_evil) == 0) and (len(self.team_love) == 0):
            print('The Evil WIN!!!')
            press_enter()
            sys.exit()
        elif (len(self.team_good) == 0) and (len(self.team_evil) == 0) and (len(self.team_love) == 0):
            print('The Lovers WIN!!!')
            press_enter()
            sys.exit()
        else:
            return False






    def action_cupid(self):
        press_enter()
        self.show_player_list()
        print('\n')
        lover1_idx = int(input('Please assign Lover No. 1: '))
        lover2_idx = int(input('Please assign Lover No. 1: '))
        lover1 = self.player_list[lover1_idx - 1]
        lover2 = self.player_list[lover2_idx - 1]
        print('So, the lovers you just assigned are Player %d (%s) and Player %d (%s).'
              % (lover1_idx - 1, lover1.pid, lover2_idx - 1, lover2.pid))
        i_sure = input('Are you sure? (0 - Re-assign; 1 - Confirm) ')
        if not i_sure == '1':
            return self.action_cupid()
        self.player_list[lover1_idx - 1].lover = self.player_list[lover2_idx - 1]
        self.player_list[lover2_idx - 1].lover = self.player_list[lover1_idx - 1]
        if (lover1_idx in self.team_good) and (lover2_idx in self.team_good) and (self.cupid_idx in self.team_good):
            if (lover1_idx in self.team_evil) and (lover2_idx in self.team_evil) and (self.cupid_idx in self.team_evil):
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
        print('Now poke the lovers!')
        press_enter()
        clear_screen()
        print('Now the lovers look into each others\' eyes!')
        press_enter()

    def action_evil(self):
        press_enter()
        self.show_player_list()
        kill_idx = int(input('Please select a player you want to KILL tonight! '))
        i_sure = input('Are you sure? (0 - Redo; 1 - Confirm) ')
        if not i_sure == '1':
            return self.action_evil()
        clear_screen()
        press_enter()
        return kill_idx

    def action_guard(self):
        press_enter()
        self.show_player_list()
        guard_idx = int(input('Please select a player you want to GUARD tonight! '))
        i_sure = input('Are you sure? (0 - Redo; 1 - Confirm) ')
        if not i_sure == '1':
            return self.action_guard()
        clear_screen()
        press_enter()
        return guard_idx

    def action_witch(self):
        press_enter()
        self.show_player_list()
        print('Tonight, the player killed by the evil is Player %d (%s).'
              % (self.kill_idx[-1], self.player_list[self.kill_idx[-1] + 1].pid))
        heal_idx = int(input('Are you gonna HEAL him/her? (0 - Nope; 1 - Yep!) ')) * self.kill_idx[-1]
        poison_idx = int(input('Which player are you gonna POISON tonight? (0 - None) '))
        i_sure = input('Are you sure? (0 - Redo; 1 - Confirm) ')
        if not i_sure == '1':
            return self.action_witch()
        clear_screen()
        press_enter()
        return heal_idx, poison_idx

#
#
# def init_player_list(role_list, pid_list, n_player):
#     for i_player in range(game.n_player):
#         _player = Player()
#         pid, role1, role2 = _player.player_input(pid_list, role_list, i_player + 1)
#         _player.assign(pid, len(player_list) + 1, role1, role2)
#         player_list.append(_player)
#     return player_list
#
#
# def show_player_list_all(player_list):
#     clear_screen()
#     n_player = len(player_list)
#     for i_player in range(n_player):
#         _player = player_list[i_player]
#         print('Player %2i  |  %15s  | %15s  | %15s' % (_player.idx, _player.pid, _player.role1, _player.role2))
#
#
# def show_player_list(player_list):
#     clear_screen()
#     n_player = len(player_list)
#     for i_player in range(n_player):
#         _player = player_list[i_player]
#         print('Player %2i    %15s' % (_player.idx, _player.pid))
#
#
# def demo_init_player_list(role_list, pid_list, n_player):
#     player_list = []
#     _pid_idx_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
#     _role1_idx_list = [2, 8, 3, 8, 4, 5, 6, 7, 8]
#     _role2_idx_list = [8, 8, 8, 1, 8, 8, 8, 8, 2]
#     for i_player in range(n_player):
#         _player = Player()
#         _player.assign(pid_list[_pid_idx_list[i_player] - 1], i_player + 1,
#                        role_list[_role1_idx_list[i_player] - 1], role_list[_role2_idx_list[i_player] - 1])
#         player_list.append(_player)
#     return player_list


def press_enter():
    input('Press Enter to Continue')


def clear_screen():
    os.system('clear')

#
# def first_night(player_list):
#     clear_screen()
#     print('Everybody, close your eyes!')
#     press_enter()
#     action_cupid(player_list)

    # for player in player_list:
    #     if not player.lover == None:
    #         print(player.pid, player.lover.pid, player.lover.lover.pid)
    # print(player_list)

#
# def action_cupid(player_list):
#     clear_screen()
#     print('Cupid, open your eyes')
#     press_enter()
#     show_player_list(player_list)
#     print('\n')
#     lover1_idx = int(input('Please assign Lover No. 1: '))
#     lover2_idx = int(input('Please assign Lover No. 1: '))
#     lover1 = player_list[lover1_idx - 1]
#     lover2 = player_list[lover2_idx - 1]
#     print('So, the lovers you just assigned are Player %d (%s) and Player %d (%s).'
#           % (lover1_idx-1, lover1.pid, lover2_idx-1, lover2.pid))
#     i_sure = input('Are you sure? (0 - Re-assign; 1 - Confirm) ')
#     if not i_sure == '1':
#         return action_cupid(player_list)
#     player_list[lover1_idx - 1].lover = player_list[lover2_idx - 1]
#     player_list[lover2_idx - 1].lover = player_list[lover1_idx - 1]
#     clear_screen()
#     print('Now poke the lovers!')
#     press_enter()
#     clear_screen()
#     print('Now the lovers look into each others\' eyes!')
#     press_enter()
#     return player_list




def main():


    from gtts import gTTS
    import pygame
    import time

    # tts = gTTS(text='Elder, wake up!', lang='en')
    # tts = gTTS(text='吕雅愫 大坏宝', lang='zh')
    tts = gTTS(text='新华网北京3月8日电 3月8日上午，中共中央总书记、国家主席、中央军委主席习近平来到十二届全国人大五次会议四川代表团参加审议', lang='zh')
    # tts = gTTS(text = '虎扑体育讯 北京时间3月8日凌晨3:45，16-17赛季欧洲冠军联赛1/8决赛次回合的一场大战在酋长球场正式打响，阿森纳坐镇主场迎战拜仁慕尼黑。上半场沃尔科特小角度爆射得手，不过总比分阿森纳2-5落后拜仁。下半场莱万多夫斯基进球，罗本和科斯塔各入一球，比达尔双响。最终拜仁5-1阿森纳，总比分10-2进入下一轮，阿森纳则是连续7年止步淘汰赛首轮。', lang='zh')
    tts.save("good.mp3")
    pygame.init()
    pygame.mixer.music.load("good.mp3")
    pygame.mixer.music.play()
    print('abcde')

    time.sleep(33)
    return




main()