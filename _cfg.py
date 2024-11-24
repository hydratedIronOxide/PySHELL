import json
import os

LOCATION = os.path.dirname(os.path.abspath(__file__))
os.chdir(LOCATION)
CONFIG_PATH = os.path.abspath("data.json")

class CfgModes:
    R = {0: "qp", 1: "qc", 2: "cfg"}
    W = {3: "qp", 4: "qc", 5: "cfg"}
    MODE_COUNT = 6

    @staticmethod
    def check_mode(mode):
        return 0 <= mode <= CfgModes.MODE_COUNT and isinstance(mode, int)

    @staticmethod
    def get_mode(mode):
        if CfgModes.rw(mode) == "R":
            return CfgModes.R.get(mode)
        else:
            return CfgModes.W.get(mode)

    @staticmethod
    def rw(mode):
        return "R" if mode <= 2 else "W"

class Cfg:
    def __init__(self, mode: int):
        if not CfgModes.check_mode(mode): raise NotImplementedError()
        self.mode = CfgModes.get_mode(mode)
        self.rw = CfgModes.rw(mode)
        with open(CONFIG_PATH, "r") as cfg:
            self.data: dict[str: dict[str: str]] = json.load(cfg)

    def __call__(self, *args, **kwargs):
        ...

    def __getitem__(self, item):
        if self.rw == "W": raise NotImplementedError()
        return self.data.get(self.mode).get(item, None)

    def k(self):
        if self.rw == "W": raise NotImplementedError()
        a = self.data.get(self.mode)
        return list(a.keys())

    def v(self):
        if self.rw == "W": raise NotImplementedError()
        a = self.data.get(self.mode)
        return list(a.values())
