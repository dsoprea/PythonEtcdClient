class CommonOps(object):
    def validate_path(self, path):
        if path[0] != '/':
            raise ValueError("Path [%s] should've been absolute." % (path))

    def get_fq_node_path(self, path):
        self.validate_path(path)

        return ('/keys' + path)
