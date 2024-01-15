import argparse
import configparser
import logging
import os
import signal
import sys
import time


class NetworkdResolver():
    def __init__(self, args):
        self.logger = self._init_logger()

        if not os.path.exists(args.settings):
            self.logger.error("Settings file not found")
            sys.exit(0)

        signal.signal(signal.SIGTERM, self._handle_sigterm)
        self.config = configparser.ConfigParser()
        self.config.read(args.settings)

        if not self.config.has_option("DEFAULT", "redirect"):
            self.logger.error("No redirect option in settings file")
            sys.exit(0)
        if not self.config.has_option("DEFAULT", "redirect"):
            self.logger.error("No redirect option in settings file")
            sys.exit(0)
        if not self.config.has_option("DEFAULT", "host_file"):
            self.logger.error("No host_file option in settings file")
            sys.exit(0)
        if not self.config.has_option("DEFAULT", "saved_file"):
            self.logger.error("No saved_file option in settings file")
            sys.exit(0)

        self.redirect = self.config["DEFAULT"]["redirect"]
        self.url_list_file = self.config["DEFAULT"]["url_list_file"]
        self.host_file = self.config["DEFAULT"]["host_file"]
        self.saved_host = self.config["DEFAULT"]["saved_file"]

        self.logger.info("Networkd-Resolver instance created")

    def _init_logger(self, ):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(logging.Formatter('%(levelname)8s | %(message)s'))
        logger.addHandler(stdout_handler)
        return logger

    def start(self):
        try:
            self._copy_content(self.host_file, self.saved_host)

            sites_to_be_blocked = self._fetch_urls()

            current_data = self._get_last_modified_dict(self.host_file)
            self._check_content(self.host_file, sites_to_be_blocked)

            while True:
                new_data = self._get_last_modified_dict(self.host_file)
                if new_data != current_data:
                    self._check_content(self.host_file, sites_to_be_blocked)
                    current_data = new_data
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.logger.warning('Keyboard interrupt (SIGINT) received...')
            self.stop()

    def stop(self):
        self.logger.info('Cleaning up...')
        self._copy_content(self.saved_host, self.host_file)
        os.remove(self.saved_host)
        sys.exit(0)

    def _handle_sigterm(self, sig, frame):
        self.logger.warning('SIGTERM received...')
        self.stop()

    def _fetch_urls(self):
        url_list = list()
        with open(self.url_list_file) as file:
            url_list = [self.redirect + " " + line.rstrip() for line in file]
        return url_list

    def _get_last_modified_dict(self, file_path: str) -> float:
        return os.stat(file_path).st_mtime

    def _copy_content(self, source_path: str, destination_path: str):
        with open(source_path, 'r') as source, open(destination_path, 'w') as destination:
            for line in source:
                destination.write(line)

    def _check_content(self, file_path: str, sites_to_be_blocked: list):
        with open(file_path, "r+") as host_file:
            hosts = host_file.readlines()
            for site in sites_to_be_blocked:
                if site not in hosts:
                    host_file.write(site + '\n')


############
#   MAIN   #
############


class NetworkdResolverArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        super().print_help()
        print("\nHomepage: https://gitlab.univ-lr.fr/jmaitr03\r\nAuthor: Julien Maitre <julien.maitre@univ-lr.fr>\r\n")
        sys.exit()

def main():
    arg_parser = NetworkdResolverArgumentParser(usage="%(prog)s [options]")
    arg_parser.add_argument("-s", "--settings", type=str, default="settings", help="Path to settings file", required=False)

    args = arg_parser.parse_args()

    network_resolver = NetworkdResolver(args)
    network_resolver.start()


if __name__ == "__main__":
    main()
