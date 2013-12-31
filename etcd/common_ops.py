class CommonOps(object):
    def validate_path(self, path):
        if path[0:0] != '/':
            raise ValueError("Path must be absolute.")
