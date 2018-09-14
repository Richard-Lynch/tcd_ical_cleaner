#!/usr/local/bin/python3

import json

from ics import Calendar


class Event():
    def __init__(self, event):
        self.ics = event

    @property
    def ics(self):
        return self._ics

    @ics.setter
    def ics(self, value):
        self._ics = value
        self.parse_name()
        self.parse_description()
        self.parse_location()
        self.reformat_event()

    def parse_name(self):
        split_name = [item.strip() for item in self._ics.name.split('-')]
        self.code = split_name[0]
        self.title = split_name[1]

    def parse_description(self):
        parsed = [
            line.split(':')[1].strip()
            for line in self._ics.description.split('\n')
            if line and ':' in line
        ]
        self.event_type = parsed[0]
        self.lecturer = parsed[1]
        self.full_location = parsed[2]

    def parse_location(self):
        self.room = self.full_location.split("-")[0].strip()
        self.building = self.full_location.split("[")[-1].split("]")[0]
        if 'ICT' not in self.building:
            self.building = self.building.split()[0]

    def reformat_event(self):
        try:
            self._ics.name = f'{NAME_MAP[self.title]}'
        except KeyError:
            self._ics.name = f'{self.title}'
        self._ics.location = self.location
        self._ics.description = self.description

    @property
    def detail(self):
        return f'{self.title} - {self.code}'

    @property
    def description(self):
        return "\n".join([
            f'{self.detail}', f'Event Type: {self.event_type}',
            f'Lecturer: {self.lecturer}', f'Location: {self.full_location}'
        ])

    @property
    def location(self):
        return f'{self.building}: {self.room}'


if __name__ == '__main__':
    conf = json.loads(open("conf.json").read())

    input_filename = conf["input_filename"]
    output_filename = conf["output_filename"]
    NAME_MAP = conf["name_map"]

    fixed_cal = Calendar()
    for event in Calendar(open(input_filename).read()).events:
        fixed_cal.events.add(Event(event).ics)

    open(output_filename, "w").writelines(fixed_cal)
