from tools.core import src


class SourceManager(src.SourceManager):
    def __init__(self):
        super().__init__("https://github.com/ExchangeUnion/market-maker-tools")

    def get_ref(self, version):
            return "v1.0.0"
