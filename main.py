# Write your code here
import json
# import re
from dataclasses import dataclass, field
from datetime import datetime as dt
from more_itertools import pairwise


class ExceptionBusID(Exception):
    def __str__(self):
        return "bus_id is not int!"


class ExceptionLineStartEnd(Exception):
    def __init__(self, bus_id):
        self.message = f"There are two starts or ends for the line: {bus_id}."
        super().__init__(self.message)


@dataclass
class BusStop:
    stop_id: int
    stop_name: str
    stop_type: str
    a_time: str
    # num_of_stops: int = 1


@dataclass
class BusLine:
    bus_id: int
    stops: list = field(default_factory=list)
    num_of_stops: int = 1
    start: bool = False
    end: bool = False


class BusLinesStorage:
    def __init__(self) -> None:
        self.__lst_of_lines = []

    @property
    def lst_of_lines(self) -> list:
        return [x.bus_id for x in self.__lst_of_lines]

    def __contains__(self, item: int) -> bool:
        if isinstance(item, BusLine):
            return item.bus_id in self.lst_of_lines
        elif isinstance(item, int):
            return item in self.lst_of_lines
        else:
            raise NotImplemented

    def append_update_line(self, bus_id: int, stop_id: int, stop_name: str, stop_type: str, a_time: str) -> None:
        if bus_id in self.lst_of_lines:
            bus_line = next(x for x in self.__lst_of_lines if x.bus_id == bus_id)
            bus_line.num_of_stops += 1
            bus_line.stops.append(BusStop(stop_id, stop_name, stop_type, a_time))
            if stop_type == "S":
                if bus_line.start:
                    raise ExceptionLineStartEnd(bus_id)
                bus_line.start = True
            if stop_type == "F":
                if bus_line.end:
                    raise ExceptionLineStartEnd(bus_id)
                bus_line.end = True
        else:
            new_bus_line = BusLine(bus_id, [BusStop(stop_id, stop_name, stop_type, a_time)])
            if stop_type == "S":
                new_bus_line.start = True
            if stop_type == "F":
                new_bus_line.end = True
            self.__lst_of_lines.append(new_bus_line)

    def show_report_line_names(self) -> None:
        print("Line names and number of stops:")
        for i in self.__lst_of_lines:
            print(f"bus_id: {i.bus_id}, stops: {i.num_of_stops}")

    def show_report_bus_lines(self) -> None:
        check_start_end = [x for x in self.__lst_of_lines if x.start is False or x.end is False]
        if check_start_end:
            for i in check_start_end:
                print(f"There is no start or end stop for the line: {i.bus_id}.")
        else:
            start_stops = set(stop.stop_name for line in self.__lst_of_lines for stop in line.stops if stop.stop_type == "S")
            start_stops = sorted(start_stops)
            transfer_stops = [stop.stop_name for line in self.__lst_of_lines for stop in line.stops]
            transfer_stops = set(stop_name for stop_name in transfer_stops if transfer_stops.count(stop_name) > 1)
            transfer_stops = sorted(transfer_stops)
            end_stops = set(stop.stop_name for line in self.__lst_of_lines for stop in line.stops if stop.stop_type == "F")
            end_stops = sorted(end_stops)
            print(f"""Start stops: {len(start_stops)} {start_stops}
Transfer stops: {len(transfer_stops)} {transfer_stops}
Finish stops: {len(end_stops)} {end_stops}""")

    def show_report_arrival_time(self):
        buses = sorted(self.__lst_of_lines, key=lambda x: x.bus_id)

        wrong_arrival_time = []

        for bus in buses:
            for curr_stop, next_stop in pairwise(bus.stops):
                curr_a_time = dt.strptime(curr_stop.a_time, "%H:%M")
                next_a_time = dt.strptime(next_stop.a_time, "%H:%M")
                if curr_a_time > next_a_time:
                    wrong_arrival_time.append((bus.bus_id, next_stop.stop_name))
                    break

        if not wrong_arrival_time:
            print("Arrival time test:\nOK")
        else:
            print("Arrival time test:")
            for bus_id, a_time in wrong_arrival_time:
                print(f"bus_id line {bus_id}: wrong time on station {a_time}")

    def show_report_bus_stops(self) -> None:
        extracted_bus_stops = [bus_stop for line in self.__lst_of_lines for bus_stop in line.stops]
        bus_stops_names = [bus_stop.stop_name for bus_stop in extracted_bus_stops]
        extracted_bus_stops = [bus_stop for bus_stop in extracted_bus_stops if bus_stops_names.count(bus_stop.stop_name) > 1]

        wrong_stop_type = set()
        for stop in extracted_bus_stops:
            if stop.stop_type == "O":
                wrong_stop_type.add(stop.stop_name)

        if wrong_stop_type:
            print("On demand stops test:")
            print(f"Wrong stop type: {sorted(wrong_stop_type)}")
        else:
            print(print("On demand stops test:"))
            print("OK")


class DataOperator:
    def __init__(self, data) -> None:
        self.data = data
        self.bus_lines_storage = BusLinesStorage()

    def parse_bus_lines(self) -> None:
        for i in self.data:
            bus_id = i.get("bus_id")
            stop_id = i.get("stop_id")
            stop_name = i.get("stop_name")
            stop_type = i.get("stop_type")
            a_time = i.get("a_time")
            if isinstance(bus_id, int):
                self.bus_lines_storage.append_update_line(bus_id, stop_id, stop_name, stop_type, a_time)
                continue
            raise ExceptionBusID

    def report_line_names(self) -> BusLinesStorage.show_report_line_names:
        return self.bus_lines_storage.show_report_line_names()

    def report_bus_lines(self) -> BusLinesStorage.show_report_bus_lines:
        return self.bus_lines_storage.show_report_bus_lines()

    def report_a_time(self) -> BusLinesStorage.show_report_arrival_time:
        return self.bus_lines_storage.show_report_arrival_time()

    def report_stop_type(self) -> BusLinesStorage.show_report_bus_stops:
        return self.bus_lines_storage.show_report_bus_stops()


if __name__ == "__main__":
    DATA = input()
    DATA = json.loads(DATA)

    data_operator = DataOperator(DATA)

    data_operator.parse_bus_lines()

    # data_operator.report_line_names()
    # data_operator.report_bus_lines()
    # data_operator.report_a_time()
    data_operator.report_stop_type()

    # MISTAKES_COUNTER.show_mistakes()
    # class MistakesCounter():
    #     def __init__(self):
    #         # self.bus_id = 0
    #         # self.stop_id = 0
    #         self.stop_name = 0
    #         # self.next_stop = 0
    #         self.stop_type = 0
    #         self.a_time = 0
    #
    #     def show_mistakes(self):
    #         mistakes = vars(self)
    #         num_of_mistakes = sum(mistakes.values())
    #
    #         print(f"Format validation: {num_of_mistakes} errors")
    #         for k, v in mistakes.items():
    #             print(f"{k}: {v}")

    # MISTAKES_COUNTER = MistakesCounter()

    # STOP_NAME_PAT = r"^[A-Z]\w+\s(\w+\s)*(Road|Avenue|Boulevard|Street)$"
    # STOP_TYPE_PAT = r"^(S|O|F|)$"
    # DATE_FORMAT_PAT = r"^([01]\d|2[0-3]):[0-5]\d$"
    #
    # STOP_NAME = re.compile(STOP_NAME_PAT)
    # STOP_TYPE = re.compile(STOP_TYPE_PAT)
    # DATE_FORMAT = re.compile(DATE_FORMAT_PAT)

    # for i in DATA:
        # bus_id = i.get("bus_id")
        # stop_id = i.get("stop_id")
        # stop_name = i.get("stop_name")
        # next_stop = i.get("next_stop")
        # stop_type = i.get("stop_type")
        # a_time = i.get("a_time")

        # if not bus_id or type(bus_id) != int:
        #     MISTAKES_COUNTER.bus_id += 1
        # if not stop_id or type(stop_id) != int:
        #     MISTAKES_COUNTER.stop_id += 1
        # if not STOP_NAME.match(stop_name):
        #     MISTAKES_COUNTER.stop_name += 1
        # if type(next_stop) != int:
        #     MISTAKES_COUNTER.next_stop += 1
    #     if not STOP_TYPE.match(stop_type):
    #         MISTAKES_COUNTER.stop_type += 1
    #
    #     if not DATE_FORMAT.match(a_time):
    #         MISTAKES_COUNTER.a_time += 1
    #
