import os

from core.commands.param_types import Regex
from core.decorators import command
from core.decorators import instance
from core.logger import Logger


@instance()
class LevelsController:
    def __init__(self):
        self.db = None
        self.logger = Logger('Budabot')

    def inject(self, registry):
        self.db = registry.get_instance('db')

    def start(self):
        self.db.load_sql_file('levels.sql', os.path.dirname(__file__))

    @command(command='level', params=[Regex('level', '\d*')], access_level='all', 
             description='Show level ranges')
    def level(self, _channel, _sender, reply, args):
        level = int(args[0])

        if level < 1 or level > 220:
            reply('Level must be between <highlight>1<end> and <highlight>220<end>.')
            return False

        row = self.get_level_data(level)
        reply('<highlight> | <end>'.join([
            '<white>L {level}: Team {team_min}-{team_max}<end>',
            '<cyan>PvP {pvp_min}-{pvp_max}<end>',
            '<orange>Missions {missions}<end>',
            '<blue>{tokens} token(s)<end>',
        ]).format(
            level=level,
            team_min=row.teamMin,
            team_max=row.teamMax,
            pvp_min=row.pvpMin,
            pvp_max=row.pvpMax,
            missions=row.missions,
            tokens=row.tokens,
        ))

    @command(command='missions', params=[Regex('missions', '\d*')], access_level='all', 
             description='Shows what ql missions a character can roll')
    def missions(self, _channel, _sender, reply, args):
        mission_ql = int(args[0])

        if mission_ql < 1 or mission_ql > 250:
            reply('Missions are only available between QL1 and QL250.')
            return False

        levels = []
        for row in self.get_all_levels():
            if str(mission_ql) in row.missions.split(','):
                levels.append(str(row.level))

        reply('QL{ql} missions can be rolled from these levels: {levels}'.format(
            ql=mission_ql,
            levels=' '.join(levels),
        ))

    def get_level_data(self, level=None):
        return self.db.query_single('SELECT * FROM levels WHERE level = ?', [level])

    def get_all_levels(self):
        return self.db.query('SELECT * FROM levels ORDER BY level')
