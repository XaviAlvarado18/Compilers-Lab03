import sys
from antlr4 import *
from ConfRoomSchedulerLexer import ConfRoomSchedulerLexer
from ConfRoomSchedulerParser import ConfRoomSchedulerParser
from ConfRoomSchedulerListener import ConfRoomSchedulerListener
from datetime import datetime

class ConfRoomSchedulerSemanticChecker(ConfRoomSchedulerListener):
    def __init__(self):
        self.reservations = {}

    def enterReserveStat(self, ctx):
        id = ctx.reserve().ID().getText()
        date = ctx.reserve().DATE().getText()
        start_time = ctx.reserve().TIME(0).getText()
        end_time = ctx.reserve().TIME(1).getText()
        reservation_key = f"{id}_{date}_{start_time}_{end_time}"

        if not self.is_valid_time_range(start_time, end_time):
            print(f"Error: La hora de inicio {start_time} debe ser anterior a la hora de fin {end_time}")
            return

        if reservation_key in self.reservations:
            print(f"Error: Ya existe una reserva para {id} el {date} de {start_time} a {end_time}")
        else:
            self.reservations[reservation_key] = id
            print(f"Reservado: {id} para {date} de {start_time} a {end_time}")

    def enterCancelStat(self, ctx):
        id = ctx.cancel().ID().getText()
        date = ctx.cancel().DATE().getText()
        start_time = ctx.cancel().TIME(0).getText()
        end_time = ctx.cancel().TIME(1).getText()
        reservation_key = f"{id}_{date}_{start_time}_{end_time}"

        if reservation_key in self.reservations:
            del self.reservations[reservation_key]
            print(f"Cancelado: {id} para {date} de {start_time} a {end_time}")
        else:
            print(f"Error: No existe ninguna reserva para {id} el {date} de {start_time} a {end_time}")

    def enterBlank(self, ctx):
        # Ignorar líneas en blanco
        pass

    def is_valid_time_range(self, start_time, end_time):
        fmt = '%H:%M'
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)
        return start < end

def main():
    input_stream = FileStream(sys.argv[1])
    lexer = ConfRoomSchedulerLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ConfRoomSchedulerParser(stream)
    tree = parser.prog()
    
    semantic_checker = ConfRoomSchedulerSemanticChecker()
    walker = ParseTreeWalker()
    walker.walk(semantic_checker, tree)

if __name__ == '__main__':
    main()