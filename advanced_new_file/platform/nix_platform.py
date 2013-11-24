class NixPlatform():
    def split(self, path):
        return None, path

    def parse_nix_path(self, root, path):
        return "/", 1
