import logging
import os


class Shell:
    def __init__(self, config):
        self.config = config
        self._logger = logging.getLogger("launcher.Shell")

    def _write_ash_profile(self, prompt):
        template = os.path.dirname(__file__) + "/profile.ash"
        with open(template) as f:
            template = f.read()
        template = template.replace("{{prompt}}", prompt)
        ash_profile = "/root/.profile"
        with open(ash_profile, "w") as f:
            f.write(template)

    def _print_banner(self):
        banner_file = os.path.dirname(__file__) + "/banner.txt"
        with open(banner_file) as f:
            print(f.read(), flush=True, end="")

    def start(self):
        prompt = f"{self.config.network} > "
        self._write_ash_profile(prompt)
        os.system("sh -l")  # use login shell to load /etc/profile and /root/.profile
