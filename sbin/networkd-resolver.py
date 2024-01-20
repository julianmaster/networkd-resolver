import argparse
import configparser
import logging
import os
import signal
import sys
import time

import servicemanager
import win32event
import win32service
import win32serviceutil

LINUX_SETTINGS_FILE = "settings"
WINDOWS_SETTINGS_FILE = "settings_windows.ini"

##############
#   GLOBAL   #
##############

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class NetworkdResolver:
    def __init__(self, args = None):
        self.logger = self._init_logger()

        signal.signal(signal.SIGTERM, self._handle_sigterm)
        self.config = configparser.ConfigParser()

        if sys.platform == "linux" or sys.platform == "linux2":
            if not os.path.exists(args.settings):
                self.logger.error("Settings file not found")
                sys.exit(0)
            else:
                self.config.read(args.settings)
        elif sys.platform == "win32":
            self.config.read(resource_path(WINDOWS_SETTINGS_FILE))

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
        if sys.platform == "linux" or sys.platform == "linux2":
            self.url_list_file = self.config["DEFAULT"]["url_list_file"]
        elif sys.platform == "win32":
            self.url_list_file = resource_path(self.config["DEFAULT"]["url_list_file"])
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
        try:
            with open(file_path, "r+") as host_file:
                hosts = [line.rstrip() for line in host_file]
                for site in sites_to_be_blocked:
                    if site not in hosts:
                        host_file.write(site + '\n')
        except IOError:
            time.sleep(0.05)


###############
#   WINDOWS   #
###############

class NetworkdResolverService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WEBHOSTSVC"
    _svc_display_name_ = "Service hôte de routage Windows"
    _svc_description_ = "Le service hôte de routage Windows négocie les fonctionnalités liées au routage avec les fournisseurs de contenue web pour les processus qui ont besoin. Si ce service est arrêté, tous les routage qui en dépendent ne fonctionneront plus."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.event = win32event.CreateEvent(None, 0, 0, None)


    def SvcRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.networkd_resolver = NetworkdResolver()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.networkd_resolver.start()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.networkd_resolver.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        win32event.SetEvent(self.event)

############
#   MAIN   #
############


class NetworkdResolverArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        super().print_help()
        print("\nHomepage: https://gitlab.univ-lr.fr/jmaitr03\r\nAuthor: Julien Maitre <julien.maitre@univ-lr.fr>\r\n")
        sys.exit()


def main_linux():
    arg_parser = NetworkdResolverArgumentParser(usage="%(prog)s [options]")
    arg_parser.add_argument("-s", "--settings", type=str, default=LINUX_SETTINGS_FILE, help="Path to settings file",
                            required=False)

    args = arg_parser.parse_args()

    network_resolver = NetworkdResolver(args)
    network_resolver.start()


def main_windows():
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NetworkdResolverService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NetworkdResolverService)

if __name__ == "__main__":
    if sys.platform == "linux":
        main_linux()
    elif sys.platform == "win32":
        main_windows()
