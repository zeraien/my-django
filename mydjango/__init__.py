VERSION = (0,2)
# Dynamically calculate the version based on VERSION tuple
if len(VERSION)>2 and VERSION[2] is not None:
    __version__ = "%d.%d_%s" % VERSION[:3]
else:
    __version__ = "%d.%d" % VERSION[:2]

