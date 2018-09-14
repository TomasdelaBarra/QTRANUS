# -*- coding: utf-8 -*-

__ALL__ = ['TranusProject']

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

	