import shutil
import subprocess

import mss
import os
import datetime


def run(arguments):
    ps = PrintScreenCommand()
    ps.run(arguments)


class PrintScreenCommand:
    def __init__(self):
        self.arguments = None
        self.variables = {}

    def run(self, arguments):
        self.arguments = arguments
        self.parse_variables()

        original_path = self.print_screen(self.arguments.output, self.arguments.monitor)
        print(original_path)
        backup_path = self.print_screen(self.arguments.backup, -1)
        self.make_backup_copy(original_path)

        if arguments.rect:
            cmd = f"ihl rect -p {original_path}"
            if arguments.rect_minimize:
                subprocess.Popen(f"{cmd} -z")
            else:
                subprocess.Popen(cmd)

    def parse_variables(self):
        for raw_variable in self.arguments.variables:
            if "=" in raw_variable:
                split_parts = raw_variable.split("=")
                self.variables[split_parts[0]] = split_parts[1]

    def evaluate_datetime_in_path(self, template):
        return datetime.datetime.now().strftime(template)

    def evaluate_variables_in_path(self, template):
        result = template
        for key in self.variables:
            result = result.replace("{%s}" % key, self.variables[key])
        return result

    def make_backup_copy(self, path):
        backup_path = self.evaluate_datetime_in_path(self.arguments.backup_directory)
        backup_path =self.evaluate_variables_in_path(backup_path)
        self.create_directories(backup_path)
        shutil.copy2(path, backup_path)

    def create_directories(self, path):
        d = os.path.dirname(path)
        os.makedirs(d, exist_ok=True)

    def print_screen(self, template, monitor):
        with mss.mss() as sct:
            path = self.evaluate_variables_in_path(template)
            path = self.evaluate_datetime_in_path(path)
            self.create_directories(path)
            sct.shot(mon=int(monitor), output=path)
            return path