import argparse
import configparser
import logging
import os
import signal
import sys
import time


class LoadFromFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with values as f:
            parser.parse_args(f.read().split(), namespace)


class NetworkdResolver():
    def __init__(self, args):
        self.logger = self._init_logger()

        self.config = configparser.ConfigParser()
        self.config.read(args.file)

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
            host_file = self.config['DEFAULT']['HostFile']

            sites_to_be_blocked = self._fetch_urls()

            current_data = self._get_last_modified_dict(host_file)
            self._check_content(host_file, sites_to_be_blocked)

            while True:
                new_data = self._get_last_modified_dict(host_file)
                if new_data != current_data:
                    self._check_content(host_file, sites_to_be_blocked)
                    current_data = new_data
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.logger.warning('Keyboard interrupt (SIGINT) received...')
            self.stop()

    def stop(self):
        self.logger.info('Cleaning up...')

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

    def _save_previous_content(self, file_path: str, save_path: str):
        pass

    def _check_content(self, file_path: str, sites_to_be_blocked: list):
        with open(file_path, "r+") as host_file:
            hosts = host_file.readlines()
            host_file.seek(0)
            for site in sites_to_be_blocked:
                if site not in hosts:
                    host_file.write(site + '\n')


 ############
#   MAIN   #
############

arg_parser = argparse.ArgumentParser(usage="%prog [options] start|stop")


def usage():
    arg_parser.print_help()
    print("\nHomepage: http://netkiller.github.io\r\nAuthor: Julien Maitre <julien.maitre@univ-lr.fr>\r\n")
    sys.exit()


def main():
    arg_parser.add_argument("--file", type=open, action=LoadFromFile, default="network-resolver")

    args = arg_parser.parse_args()
    if not args:
        usage()

    if args.file:
        if 'start' in args:
            network_resolver = NetworkdResolver()
            network_resolver.start()
        else:
            usage()


if __name__ == "__main__":
    main()
