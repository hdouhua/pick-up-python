import os
import yaml


# please refer to example 2 at
# https://www.programcreek.com/python/example/11269/yaml.add_constructor
def get_config(config_file='c02/test_config.yaml'):
    # add direction join function when parse the yaml file
    def join(loader, node):
        seq = loader.construct_sequence(node)
        return os.path.sep.join(seq)

    # add string concatenation function when parse the yaml file
    def concat(loader, node):
        seq = loader.construct_sequence(node)
        seq = [str(tmp) for tmp in seq]
        return ''.join(seq)

    yaml.add_constructor('!join', join)
    yaml.add_constructor('!concat', concat)
    with open(config_file, 'r') as fin:
        cfg = yaml.load(fin, Loader=yaml.FullLoader)

    return cfg


if __name__ == "__main__":
    # print(os.getcwd())
    # current_dir = os.path.dirname(__file__)
    # config = get_config(os.path.join(current_dir, 'config.yaml'))

    config = get_config()

    print(config)
