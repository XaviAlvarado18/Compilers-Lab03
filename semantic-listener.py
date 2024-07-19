import sys
from antlr4 import *
from ConfRoomSchedulerLexer import ConfRoomSchedulerLexer
from ConfRoomSchedulerParser import ConfRoomSchedulerParser
from ConfRoomSchedulerListener import ConfRoomSchedulerListener
from datetime import datetime

class ConfRoomSchedulerSemanticChecker(ConfRoomSchedulerListener):
    def __init__(self):
        self.reservations = {}  # Dict to keep track of active reservations

    def enterReserveStat(self, ctx):
        user = ctx.reserve().USER().getText()
        id = ctx.reserve().ID().getText()
        date = ctx.reserve().DATE().getText()
        start_time = ctx.reserve().TIME(0).getText()
        end_time = ctx.reserve().TIME(1).getText()
        reservation_key = f"{id}_{date}_{start_time}_{end_time}"

        # Validar formato de la hora
        if not self.is_valid_time_format(start_time) or not self.is_valid_time_format(end_time):
            print(f"Error: La hora de inicio o fin no tiene un formato válido.")
            return

        try:
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
        except ValueError:
            print(f"Error: La hora de inicio '{start_time}' o fin '{end_time}' no es válida.")
            return

        if not self.is_valid_time_range(start_time, end_time):
            print(f"Error: La hora de inicio {start_time} debe ser anterior a la hora de fin {end_time}")
            return

        # Verificar solapamiento con reservas existentes
        if self.is_conflicting_reservation(id, date, start_time, end_time):
            print(f"Error: La reserva se solapa con una reserva existente para {id} el {date} de {start_time} a {end_time}")
        else:
            self.reservations[reservation_key] = (id, user)
            print(f"Reservado: {id} para {date} de {start_time} a {end_time} por {user}")

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

    def is_valid_time_format(self, time_str):
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    def is_conflicting_reservation(self, room_id, date, start_time, end_time):
        fmt = '%H:%M'
        new_start = datetime.strptime(start_time, fmt)
        new_end = datetime.strptime(end_time, fmt)
        
        for key, value in self.reservations.items():
            res_id, _ = value
            res_date, res_start, res_end = key.split('_')[1:]
            res_start = datetime.strptime(res_start, fmt)
            res_end = datetime.strptime(res_end, fmt)
            
            if res_id == room_id and res_date == date:
                if (new_start < res_end and new_end > res_start):
                    return True
        return False

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
