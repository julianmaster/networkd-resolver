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

        self.config = configparser.ConfigParser()
        self.config.read(args.settings)
        self.host_file = self.config['DEFAULT']['HostFile']
        self.saved_host = self.config['DEFAULT']['SavedHost']

        signal.signal(signal.SIGTERM, self._handle_sigterm)

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

        sys.exit(0)

    def _handle_sigterm(self, sig, frame):
        self.logger.warning('SIGTERM received...')
        self.stop()

    def _fetch_urls(self):
        url_list = list()
        with open('../conf/urllist.txt') as file:
            url_list = [self.config['DEFAULT']['Redirect'] + " " + line.rstrip() for line in file]
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

arg_parser = argparse.ArgumentParser(usage="%(prog)s [options] start|stop")


def usage():
    arg_parser.print_help()
    print("\nHomepage: https://gitlab.univ-lr.fr/jmaitr03\r\nAuthor: Julien Maitre <julien.maitre@univ-lr.fr>\r\n")
    sys.exit()


def main():
    arg_parser.add_argument("--settings", default="settings")
    arg_parser.add_argument("state", choices=["start", "stop"], help="")

    args = arg_parser.parse_args()
    print(args)
    if not args:
        usage()

    if args.settings:
        if args.state == 'start':
            network_resolver = NetworkdResolver(args)
            network_resolver.start()
        else:
            usage()


if __name__ == "__main__":
    main()
