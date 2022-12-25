import sys

class prepend_path:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            sys.path.remove(self.path)
        except:
            pass

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
