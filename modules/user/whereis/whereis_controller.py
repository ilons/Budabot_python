from core.decorators import instance, command, event, timerevent
from core.db import DB
from core.text import Text
from core.command_params import Text
from core.chat_blob import ChatBlob
import os


@instance()
class WhereisController:
    def __init__(self):
        pass

    def inject(self, registry):
        self.db: DB = registry.get_instance("db")
        self.text: Text = registry.get_instance("text")

    def start(self):
        self.db.load_sql_file("whereis.sql", os.path.dirname(__file__))

    @command(command="whereis", params=[Text("search")], access_level="all",
             description="Find locations of NPCs and places")
    def handle_whereis_cmd(self, channel, sender, reply, args):
        search = args[1]
        data = self.db.query("SELECT w.playfield_id, w.name, w.answer, w.xcoord, w.ycoord, p.short_name FROM whereis w "
                             "LEFT JOIN playfields p ON w.playfield_id = p.id "
                             "WHERE name <ENHANCED_LIKE> ? OR keywords <ENHANCED_LIKE> ?",
                             [search, search])
        count = len(data)
        if count > 0:
            blob = ""
            for row in data:
                blob += "<header2>" + row.name + "<end>\n" + row.answer
                if row.playfield_id and row.xcoord and row.ycoord:
                    blob += " " + self.text.make_chatcmd("waypoint: %sx%s %s" % (row.xcoord, row.ycoord, row.short_name),
                                                         "/waypoint %s %s %d" % (row.xcoord, row.ycoord, row.playfield_id))
                blob += "\n\n"
            reply(ChatBlob("Whereis '%s' (%d)" % (search, count), blob))
        else:
            reply("Could not find any results for your search.")

    @timerevent(budatime="10s", description="How often we print stuff")
    #@event(event_type="buddy_logon", description="Show buddy login")
    def handle_connect_event(self, event_type, event_data):
        # print(event_type)
        pass