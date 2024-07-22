import sys
from antlr4 import *
from ConfRoomSchedulerLexer import ConfRoomSchedulerLexer
from ConfRoomSchedulerParser import ConfRoomSchedulerParser
from ConfRoomSchedulerListener import ConfRoomSchedulerListener
from datetime import datetime, timedelta

class ConfRoomSchedulerSemanticChecker(ConfRoomSchedulerListener):
    MAX_DURATION = 120
    NOTIFICATION_TIME = timedelta(hours=1)  # Notificación 1 hora antes de la reserva

    def __init__(self):
        self.reservations = {}  # Dict to keep track of active reservations
        self.next_reservations = []  # List to keep track of upcoming reservations

    def enterReserveStat(self, ctx):
        try:
            user = ctx.reserve().USER().getText()
            id = ctx.reserve().ID().getText()
            date = ctx.reserve().DATE().getText()
            start_time = ctx.reserve().TIME(0).getText()
            end_time = ctx.reserve().TIME(1).getText()
        except AttributeError as e:
            print(f"Error: Faltan datos en la reserva ({e})")
            return

        if not self.is_valid_time_format(start_time) or not self.is_valid_time_format(end_time):
            print("Error: La hora de inicio o fin no tiene un formato válido.")
            return

        try:
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
            reservation_date = datetime.strptime(date, '%d/%m/%Y')
            reservation_start = datetime.combine(reservation_date, start)
            reservation_end = datetime.combine(reservation_date, end)
        except ValueError:
            print(f"Error: La hora de inicio '{start_time}' o fin '{end_time}' no es válida.")
            return

        if not self.is_valid_time_range(start, end):
            print(f"Error: La hora de inicio {start_time} debe ser anterior a la hora de fin {end_time}")
            return

        if self.is_exceeding_max_duration(start, end):
            print(f"Error: La reserva excede el tiempo máximo permitido de {self.MAX_DURATION} minutos")
            return

        if self.is_conflicting_reservation(id, date, reservation_start, reservation_end):
            print(f"Error: La reserva se solapa con una reserva existente para {id} el {date} de {start_time} a {end_time}")
        else:
            reservation_key = f"{id}_{date}_{start_time}_{end_time}"
            self.reservations[reservation_key] = (id, user, reservation_start, reservation_end)
            print(f"Reservado: {id} para {date} de {start_time} a {end_time} por {user}")
            self.check_for_notifications(reservation_start)

    def enterCancelStat(self, ctx):
        try:
            id = ctx.cancel().ID().getText()
            date = ctx.cancel().DATE().getText()
            start_time = ctx.cancel().TIME(0).getText()
            end_time = ctx.cancel().TIME(1).getText()
        except AttributeError as e:
            print(f"Error: Faltan datos en la cancelación ({e})")
            return

        reservation_key = f"{id}_{date}_{start_time}_{end_time}"

        if reservation_key in self.reservations:
            del self.reservations[reservation_key]
            print(f"Cancelado: {id} para {date} de {start_time} a {end_time}")
        else:
            print(f"Error: No existe ninguna reserva para {id} el {date} de {start_time} a {end_time}")

    def enterListStat(self, ctx):
        if not self.reservations:
            print("No hay reservas existentes")
        else:
            print("Reservas existentes:")
            for key, (id, user, start, end) in self.reservations.items():
                _, date, start_time, end_time = key.split('_')
                print(f"{id} para {date} de {start_time} a {end_time} por {user}")

    def enterReprogramStat(self, ctx):
        try:
            id = ctx.reprogram().ID().getText()
            date = ctx.reprogram().DATE().getText()
            old_start_time = ctx.reprogram().TIME(0).getText()
            old_end_time = ctx.reprogram().TIME(1).getText()
            new_start_time = ctx.reprogram().TIME(2).getText()
            new_end_time = ctx.reprogram().TIME(3).getText()
        except AttributeError as e:
            print(f"Error: Faltan datos en la reprogramación ({e})")
            return

        old_reservation_key = f"{id}_{date}_{old_start_time}_{old_end_time}"
        new_reservation_key = f"{id}_{date}_{new_start_time}_{new_end_time}"

        if old_reservation_key not in self.reservations:
            print(f"Error: No existe ninguna reserva para {id} el {date} de {old_start_time} a {old_end_time}")
            return

        try:
            new_start = datetime.strptime(new_start_time, '%H:%M').time()
            new_end = datetime.strptime(new_end_time, '%H:%M').time()
            reservation_date = datetime.strptime(date, '%d/%m/%Y')
            reservation_start = datetime.combine(reservation_date, new_start)
            reservation_end = datetime.combine(reservation_date, new_end)
        except ValueError:
            print(f"Error: La nueva hora de inicio '{new_start_time}' o fin '{new_end_time}' no es válida.")
            return

        if self.is_conflicting_reservation(id, date, reservation_start, reservation_end):
            print(f"Error: La nueva reserva se solapa con otra reserva existente.")
            return

        # Eliminar la reserva antigua y agregar la nueva
        user = self.reservations[old_reservation_key][1]  # Obtener el usuario antes de eliminar
        del self.reservations[old_reservation_key]
        self.reservations[new_reservation_key] = (id, user, reservation_start, reservation_end)

        print(f"Reprogramado: {id} de {old_start_time} a {old_end_time} para {new_start_time} a {new_end_time}")

    def enterBlank(self, ctx):
        # Ignorar líneas en blanco
        pass

    def check_for_notifications(self, reservation_start):
        now = datetime.now()
        if reservation_start <= now + self.NOTIFICATION_TIME:
            print(f"Notificación: La reserva que empieza a las {reservation_start.strftime('%H:%M')} está próxima.")

    def is_valid_time_range(self, start, end):
        return start < end

    def is_valid_time_format(self, time_str):
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    def is_exceeding_max_duration(self, start, end):
        duration = datetime.combine(datetime.min, end) - datetime.combine(datetime.min, start)
        duration_minutes = duration.total_seconds() / 60
        return duration_minutes > self.MAX_DURATION

    def is_conflicting_reservation(self, room_id, date, new_start, new_end):
        for key, value in self.reservations.items():
            res_id, _, res_start, res_end = value
            res_date, res_start_time, res_end_time = key.split('_')[1:]
            res_start = datetime.combine(datetime.strptime(res_date, '%d/%m/%Y'), datetime.strptime(res_start_time, '%H:%M').time())
            res_end = datetime.combine(datetime.strptime(res_date, '%d/%m/%Y'), datetime.strptime(res_end_time, '%H:%M').time())

            if res_id == room_id and date == res_date:
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