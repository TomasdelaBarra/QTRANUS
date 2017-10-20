from __future__ import unicode_literals

import os
import re
import csv
import glob

__ALL__ = ['TranusProject', 'TranusProjectValidationError']

# constants definition... from 0 to 4

SECTION_IDENTIFICATION, SECTION_SCENARIOS, SECTION_MODEL, SECTION_SEPARATOR, SECTION = range(5)


def extract_values(line):
    return re.findall(r"\'(.+?)\'", line)


class Identification(object):
    @staticmethod
    def load(lines):
        identification = Identification()
        identification.code, identification.name = Identification.parse_lines(lines)
        return identification

    def validate(self):
        pass

    @staticmethod
    def parse_lines(lines):
        values = extract_values(lines[1])
        return list(values)

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


class Model(object):
    @staticmethod
    def load(lines):
        return Model()

    def validate(self):
        pass


class Scenarios(object):

    def __init__(self, root):
        self.root = root
        self.results = {}
        self.scenarios_cache = {}

    @staticmethod
    def load(lines):
        nodes = Scenarios.parse_lines(lines)
        root = Scenarios.create_tree(nodes)
        return Scenarios(root)

    def validate(self):
        pass

    @staticmethod
    def parse_lines(lines):
        nodes = {}
        for line in lines[1:]:
            values = map(lambda v: v.strip(), extract_values(line))
            nodes[values[0]] = {
                'name': values[1],
                'prev': values[2] if values[2] else None
            }
        return nodes

    @staticmethod
    def create_tree(nodes):
        scenarios = {}
        def get_or_create(code, data):
            if code is None:
                return None
            if code in scenarios:
                return scenarios[code]
            else:
                prev = data['prev']
                prev_data = nodes[prev] if prev is not None else {}
                scenarios[code] = Scenario(code, data['name'], get_or_create(prev, prev_data))
                return scenarios[code]
        root = None
        for code, data in nodes.items():
            node = get_or_create(code, data)
            if node.prev is None:
                root = node
        return root

    def load_results(self, path):
        for file_path in glob.glob(os.path.join(path, 'location_indicators_*.csv')):
            with open(file_path, 'rb') as csvfile:
                reader = csv.reader(csvfile)
                headers = map(lambda s: s.strip(), reader.next())
                for line in reader:
                    line = map(lambda s: s.strip(), line)
                    line = dict(zip(headers, line))
                    scenario_code = line['Scen']
                    scenario = self.get_scenario(scenario_code)
                    if scenario is None:
                        raise Exception
                    floats = dict(map(lambda t: (t[0], float(t[1])), filter(lambda t: t[0] not in ('Scen', 'Sector', 'Zone'), line.items())))
                    line.update(floats)
                    scenario.update_results(line)

    def get_scenario(self, code):
        scenario = self.scenarios_cache.get(code)
        if scenario is None:
            scenario = self.root.find(code)
            self.scenarios_cache[code] = scenario
        return scenario

    def __str__(self):
        return str(self.root)


class Scenario(object):
    code = None
    name = None
    prev = None
    children = None
    results = []

    def __init__(self, code, name, prev):
        self.code = code
        self.name = name
        self.prev = prev
        self.children = []
        if self.prev is not None:
            self.prev.children.append(self)

    def find(self, code):
        if self.code == code:
            return self
        for child in self.children:
            result = child.find(code)
            if result is not None:
                return result
        return None

    def update_results(self, data):
        self.results.append(data)

    def get_sectors(self):
        return set(map(lambda r: r['Sector'], self.results))

    def __str__(self):
        if self.children:
            return "{code} -> ({children})".format(children=", ".join(map(str, self.children)), code=self.code)
        return "{code}".format(code=self.code)

    def __repr__(self):
        return "<Scenario({code})>\n".format(code=self.code)


class TranusProject(object):
    scenarios = None
    identification = None
    model = None

    @staticmethod
    def load_project(file_path):
        project = TranusProject()
        current_section = None
        section_lines = None
        with open(file_path, 'r') as project_file:
            for line in project_file.readlines():
                section = TranusProject.get_section(line)
                if section in (SECTION_IDENTIFICATION, SECTION_SCENARIOS, SECTION_MODEL):
                    if section_lines is not None:
                        project.add_lines_to_section(section_lines, current_section)
                    current_section = section
                    section_lines = []
                elif section == SECTION and section_lines is not None:
                    section_lines.append(line)
            project.add_lines_to_section(section_lines, current_section)
        project.validate()
        project.scenarios.load_results(os.path.dirname(file_path))
        project.path = file_path
        return project

    @staticmethod
    def get_section(line):
        if line.startswith('1.0'):
            return SECTION_IDENTIFICATION
        if line.startswith('2.0'):
            return SECTION_SCENARIOS
        if line.startswith('3.0'):
            return SECTION_MODEL
        if line.startswith('*'):
            return SECTION_SEPARATOR
        return SECTION

    def validate(self):
        try:
            self.identification.validate()
            self.scenarios.validate()
            self.model.validate()
        except AttributeError as e:
            raise TranusProjectValidationError()

    def add_lines_to_section(self, lines, section):
        if section == SECTION_IDENTIFICATION:
            self.identification = Identification.load(lines)
        elif section == SECTION_SCENARIOS:
            self.scenarios = Scenarios.load(lines)
        elif section == SECTION_MODEL:
            self.model = Model.load(lines)

    def __str__(self):
        return self.identification.name

    def __repr__(self):
        return "<TranusProject: {0}>".format(self.identification)


class TranusProjectValidationError(Exception):
    pass
