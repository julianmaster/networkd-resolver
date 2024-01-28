import argparse
import configparser
import logging.handlers
import os
import signal
import sys
import time

import servicemanager
import win32event
import win32service
import win32serviceutil

if sys.platform == "win32":
    PROCESS_DATA_PATH = os.getenv("LOCALAPPDATA") + "/webhostsvc/"
    LOG_FILE_PATH = PROCESS_DATA_PATH + "process.log"
else:
    PROCESS_DATA_PATH = "/var/log/networkd-resolver/"
    LOG_FILE_PATH = PROCESS_DATA_PATH + "process.log"

LINUX_SETTINGS_FILE = "settings"
WINDOWS_SETTINGS_FILE = "settings_windows.ini"

###########
#   LOG   #
###########

def _init_logger():
    global mylogger
    if not os.path.exists(PROCESS_DATA_PATH):
        os.mkdir(PROCESS_DATA_PATH)
    mylogger = logging.getLogger("NetworkdResolver")
    mylogger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_FILE_PATH, maxBytes=10485760, backupCount=2)
    formatter = logging.Formatter('%(asctime)s - %(module)-10s - %(levelname)-8s %(message)s', '%d-%m-%Y %H:%M:%S')
    handler.setFormatter(formatter)
    mylogger.addHandler(handler)


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
    def __init__(self, args=None):
        if 'mylogger' not in globals():
            _init_logger()

        self.running = False
        if sys.platform == "linux" or sys.platform == "linux2":
            signal.signal(signal.SIGTERM, self._handle_sigterm)

        self.config = configparser.ConfigParser()

        if sys.platform == "linux" or sys.platform == "linux2":
            if not os.path.exists(args.settings):
                mylogger.error("Settings file not found")
                sys.exit(0)
            else:
                self.config.read(args.settings)
        elif sys.platform == "win32":
            self.config.read(resource_path(WINDOWS_SETTINGS_FILE))

        if not self.config.has_option("DEFAULT", "redirect"):
            mylogger.error("No redirect option in settings file")
            sys.exit(0)
        if not self.config.has_option("DEFAULT", "url_list_file"):
            mylogger.error("No redirect option in settings file")
            sys.exit(0)
        if not self.config.has_option("DEFAULT", "host_file"):
            mylogger.error("No host_file option in settings file")
            sys.exit(0)
        if not self.config.has_option("DEFAULT", "saved_file"):
            mylogger.error("No saved_file option in settings file")
            sys.exit(0)

        self.redirect = self.config["DEFAULT"]["redirect"]
        if sys.platform == "linux" or sys.platform == "linux2":
            self.url_list_file = self.config["DEFAULT"]["url_list_file"]
        elif sys.platform == "win32":
            self.url_list_file = resource_path(self.config["DEFAULT"]["url_list_file"])
        self.host_file = self.config["DEFAULT"]["host_file"]
        self.saved_host = PROCESS_DATA_PATH + self.config["DEFAULT"]["saved_file"]

        mylogger.info("Networkd-Resolver instance created")

    def start(self):
        try:
            self.running = True
            mylogger.debug("Copying host file content")
            self._copy_content(self.host_file, self.saved_host)

            mylogger.debug("Fetching url list file")
            sites_to_be_blocked = self._fetch_urls()

            current_data = self._get_last_modified_dict(self.host_file)
            self._check_content(self.host_file, sites_to_be_blocked)

            mylogger.debug("Starting process...")
            while self.running:
                new_data = self._get_last_modified_dict(self.host_file)
                if new_data != current_data:
                    result = self._check_content(self.host_file, sites_to_be_blocked)
                    if result:
                        current_data = new_data
                time.sleep(0.05)
        except KeyboardInterrupt:
            mylogger.warning('Keyboard interrupt (SIGINT) received...')
            self.stop()

    def stop(self):
        running = False
        time.sleep(0.5)
        mylogger.info('Cleaning up...')
        self._copy_content(self.saved_host, self.host_file)
        mylogger.info("Removing saved host file")
        os.remove(self.saved_host)
        if sys.platform == "linux" or sys.platform == "linux2":
            sys.exit(0)

    def _handle_sigterm(self, sig, frame):
        mylogger.warning('SIGTERM received...')
        self.stop()

    def _fetch_urls(self):
        url_list = list()
        with open(self.url_list_file) as file:
            url_list = [self.redirect + " " + line.rstrip() for line in file]
        return url_list

    def _get_last_modified_dict(self, file_path: str) -> float:
        return os.stat(file_path).st_mtime

    def _copy_content(self, source_path: str, destination_path: str):
        while True:
            try:
                with open(source_path, 'r') as source, open(destination_path, 'w') as destination:
                    for line in source:
                        destination.write(line)
                return  # DO NOT REMOVE IT !! AT ALL COST !! (BASTARD !!)
            except IOError:
                time.sleep(0.05)

    def _check_content(self, file_path: str, sites_to_be_blocked: list) -> bool:
        try:
            with open(file_path, "r+") as host_file:
                hosts = [line.rstrip() for line in host_file]
                for site in sites_to_be_blocked:
                    if site not in hosts:
                        host_file.write(site + '\n')
        except IOError:
            return False
        return True


###############
#   WINDOWS   #
###############

class NetworkdResolverService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WEBHOSTSVC"
    _svc_display_name_ = "Windows Routing Service"
    _svc_description_ = "The Windows Routing Service negotiates routing-related features with web content providers for processes that require it. If this service is stopped, all routing dependent on it will cease to function."

    def __init__(self, args):
        super().__init__(args)
        if 'mylogger' not in globals():
            _init_logger()

        self.args = args
        mylogger.debug("Initializing NetworkdResolverService")
        win32serviceutil.ServiceFramework.__init__(self, args)
        mylogger.debug("Creating event...")
        self.event = win32event.CreateEvent(None, 0, 0, None)

    def SvcRun(self):
        mylogger.debug("Report starting NetworkdResolverService")
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        mylogger.debug("Creating NetworkdResolver")
        self.networkd_resolver = NetworkdResolver(self.args)
        mylogger.debug("Report running NetworkdResolverService")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.networkd_resolver.start()

    def SvcStop(self):
        mylogger.debug("Report stopping NetworkdResolverService")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.networkd_resolver.stop()
        mylogger.debug("Report stopped NetworkdResolverService")
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


if sys.platform == "linux" or sys.platform == "linux2":
    main_linux()
elif sys.platform == "win32":
    main_windows()
