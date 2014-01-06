class CommonOps(object):
    """Base-class of 'ops' modules."""

    def validate_path(self, path):
        """Validate the key that we were given.

        :param path: Key
        :type path: string

        :raises: ValueError
        """

        if path[0] != '/':
            raise ValueError("Path [%s] should've been absolute." % (path))

    def get_fq_node_path(self, path):
        """Return the full path of the given key.

        :param path: Key
        :type path: string
        """

        self.validate_path(path)

        return ('/keys' + path)
