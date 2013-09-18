import logging
import os

import argh
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import ponzi.manager


@argh.arg('--config', default=None, help='Location of the json configuration file')
def start(config):
    default_path = os.path.abspath(os.path.join("config.yaml"))
    with open(default_path, 'rb') as f:
        options = yaml.load(f, Loader)
    if config:
        logging.info("Loading user config.yaml file at: {}".format(config))
        with open(config, 'rb') as f:
            user_options = yaml.load(f, Loader)
            options.update(user_options)
    else:
        logging.warning("Using default config.yaml file")

    logging.info("Configuration Options: {}".format(options))
    ponzi.manager.Ponzi(options)


def main():
    logging.basicConfig(level="INFO")
    argh.dispatch_command(start)
