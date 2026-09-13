import os
import yaml
from yaml.constructor import ConstructorError
import glob
import logging

log = logging.getLogger(__name__)


file_pattern_cache = {}
file_path_cache = {}


class Loader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super().__init__(stream)
        Loader.add_constructor('!include', Loader.include)
        Loader.add_constructor('!import', Loader.include)

    def include(self, node):
        if isinstance(node, yaml.ScalarNode):
            return self.extractFile(self.construct_scalar(node))

        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result += self.extractFile(filename)
            return result

        elif isinstance(node, yaml.MappingNode):
            result = {}
            for k, v in self.construct_mapping(node).items():
                result[k] = self.extractFile(v)[k]
            return result

        else:
            log.error("unrecognised node type in !include statement")
            raise ConstructorError

    def extractFile(self, filename):
        file_pattern = os.path.join(self._root, filename)
        log.debug(f'Will attempt to extract schema from: {file_pattern}')
        if file_pattern in file_pattern_cache:
            log.debug(f'File pattern cache hit: {file_pattern}')
            return file_pattern_cache[file_pattern]

        data = dict()
        for file_path in glob.glob(file_pattern):
            file_path = os.path.abspath(file_path)
            if file_path in file_path_cache:
                log.debug(f'Schema cache hit: {file_path}')
                path_data = file_path_cache[file_path]
            else:
                log.debug(f'Loading schema from {file_path}')
                with open(file_path, 'r') as f:
                    path_data = yaml.load(f, Loader)
                file_path_cache[file_path] = path_data
            data.update(path_data)

        file_pattern_cache[file_pattern] = data
        return data
