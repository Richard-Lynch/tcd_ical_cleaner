#!/usr/local/bin/python3

import json
from functools import partial
from pprint import pprint as pprint_default

from ics import Calendar

pprint = partial(pprint_default, width=160)
NAME_MAP = {}


class Event():
    def __init__(self, event):
        self.ics = event

    @property
    def ics(self):
        return self._ics

    @ics.setter
    def ics(self, value):
        self._ics = value
        self.name = EventName(self._ics.name)
        self.description = EventDescription(self._ics.description)
        self.location = EventLocation(self.description.location)
        self._ics.name = self.name.formatted
        self._ics.location = self.location.formatted
        self._ics.description = self.description.formatted


class EventName:
    def __init__(self, name, sep='-'):
        self.sep = sep
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

        split_title = [item.strip() for item in self.name.split(self.sep)]
        self.code = split_title[0]
        self.title = split_title[1]

        try:
            self.formatted = f'{NAME_MAP[self.title]}'
        except KeyError:
            self.formatted = f'{self.title}'


class EventDescription:
    def __init__(self, description, sep=':'):
        self.sep = sep
        self.description = description

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

        parsed = [line for line in self.description.split('\n') if line]
        self.detail = parsed[0]

        parsed = [
            self._parse_line(line) for line in parsed[1:]
            if self._is_valid_line(line)
        ]
        self.event_type = parsed[0]
        self.lecturer = parsed[1]
        self.location = parsed[2]

        self.formatted = "\n".join([
            f'{self.detail}', f'Event Type: {self.event_type}',
            f'Lecturer: {self.lecturer}', f'Location: {self.location}'
        ])

    def _parse_line(self, line):
        return line.strip().split(self.sep)[1]

    def _is_valid_line(self, line):
        return line and self.sep in line


class EventLocation:
    def __init__(self, location):
        self.location = location

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

        self.room = self.location.split("-")[0].strip()

        if 'ICT' in self.location:
            self.building = self._ict_building()
        else:
            self.building = self._normal_building()

        self.formatted = f'{self.building}: {self.room}'

    def _normal_building(self):
        return self._ict_building().split()[0]

    def _ict_building(self):
        return self.location.split("[")[-1].split("]")[0]


if __name__ == '__main__':
    conf = json.loads(open("conf.json").read())

    input_filename = conf["input_filename"]
    output_filename = conf["output_filename"]
    NAME_MAP = conf["name_map"]

    fixed_cal = Calendar()
    for event in Calendar(open(input_filename).read()).events:
        fixed_cal.events.add(Event(event).ics)

    counter = 0
    for event in fixed_cal.events:
        print(event)
        counter += 1
        if counter > 10:
            break

    open(output_filename, "w").writelines(fixed_cal)
