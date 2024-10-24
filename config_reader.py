import yaml


class ConfigReader:
    def __init__(self, config_file, programs_file):
        self.config = self.load_yaml(config_file)
        self.programs = self.load_yaml(programs_file)

    @staticmethod
    def load_yaml(file_path):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
