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
        if not self._fixed:
            self._ics.name = self.name.formatted
            self._ics.location = self.location.formatted
            self._ics.description = self.description.formatted
            self._fixed = True
        return self._ics

    @ics.setter
    def ics(self, value):
        self._fixed = False
        self._ics = value
        self._name = None
        self._description = None
        self._location = None

    @property
    def name(self):
        if not self._name:
            self._name = EventName(self._ics.name)
        return self._name

    @property
    def description(self):
        if not self._description:
            self._description = EventDescription(self._ics.description)
        return self._description

    @property
    def location(self):
        if not self._location:
            self._location = EventLocation(self.description.location)
        return self._location


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
        self._parsed = None
        self._formatted = None

    @property
    def parsed(self):
        if not self._parsed:
            split_title = [item.strip() for item in self.name.split(self.sep)]
            self.parsed_name = {
                'code': split_title[0],
                'title': split_title[1]
            }
        return self.parsed_name

    @property
    def formatted(self):
        if not self._formatted:
            try:
                self._formatted = f'{NAME_MAP[self.parsed["title"]]}'
            except KeyError:
                self._formatted = f'{self.parsed["title"]}'
        return self._formatted


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
        self._parsed = []
        self._formatted = None
        self._detail = None
        self._event_type = None
        self._lecturer = None
        self._location = None

    @property
    def parsed(self):
        if not self._parsed:
            parsed = [line for line in self.description.split('\n') if line]
            self._parsed.append(parsed[0])
            self._parsed.append([
                self._parse_line(line) for line in parsed[1:]
                if self._is_valid_line(line)
            ])
        if len(self._parsed) < 2:
            print(self)
            raise Exception
        return self._parsed

    @property
    def event_type(self):
        if not self._event_type:
            self._event_type = self.parsed[1][0]
        return self._event_type

    @property
    def lecturer(self):
        if not self._lecturer:
            self._lecturer = self.parsed[1][1]
        return self._lecturer

    @property
    def location(self):
        if not self._location:
            self._location = self.parsed[1][2]
        return self._location

    @property
    def detail(self):
        if not self._detail:
            self._detail = self.parsed[0]
        return self._detail

    @property
    def formatted(self):
        if not self._formatted:
            self._formatted = "\n".join([
                f'{self.detail}', f'Event Type: {self.event_type}',
                f'Lecturer: {self.lecturer}', f'Location: {self.location}'
            ])
        return self._formatted

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
        self._room = None
        self._building = None
        self._formatted = None

    @property
    def room(self):
        if not self._room:
            self._room = self.location.split("-")[0].strip()
        return self._room

    @property
    def building(self):
        if not self._building:
            if 'ICT' in self.location:
                self._building = self._ict_building()
            else:
                self._building = self._normal_building()
        return self._building

    def _normal_building(self):
        return self._ict_building().split()[0]

    def _ict_building(self):
        return self.location.split("[")[-1].split("]")[0]

    @property
    def formatted(self):
        if not self._formatted:
            self._formatted = f'{self.building}: {self.room}'
        return self._formatted


if __name__ == '__main__':
    conf = json.loads(open("conf.json").read())

    input_filename = conf["input_filename"]
    output_filename = conf["output_filename"]
    NAME_MAP = conf["name_map"]

    fixed_cal = Calendar()
    for event in Calendar(open(input_filename).read()).events:
        fixed_cal.events.add(Event(event).ics)

    open(output_filename, "w").writelines(fixed_cal)
