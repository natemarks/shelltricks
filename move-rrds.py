'''
subdirs is a list of directory paths source is the existing rrd tree opath.
defautls to /opt/zenoss destinatipon is where we'll dupicate the tree under
source and move the old rrds age is the mtime value.  anything oldr than age
will get move
'''


from subprocess import PIPE, Popen


class RRDTree(object):
    '''
    RRDTree object to be managed
    '''
    def __init__(self, *args, **kwargs):
        # store all kwargs into the __dict__
        self.source = "/opt/zenoss"
        self.destination = "/tmp/moved_rrds"
        self.age = 365
        self.source_files = []
        self.created_dirs = []
        self.__dict__.update(kwargs)

    def find_files(self):
        proc = Popen(['find',
                      self.source,
                      '-type',
                      'f',
                      '-mtime',
                      '+' + str(self.age),
                      '-name',
                      'NWN-DEVICE-PING-STATS_rtt_min.rrd'],
                     stdout=PIPE)
        self.source_files = proc.communicate()[0].split()

    def handle_files(self):
        if self.source_files == []:
            self.source_files = ['/opt/zenoss/aaa/bbb/ccc/first.txt',
                                 '/opt/zenoss/aaa/bbb/ccc/third.txt',
                                 '/opt/zenoss/ddd/eee/fff/second.txt']
        for line in self.source_files:
            targ_file = self.src_file_to_dest_file(line)
            print "======================"
            print "MOVING: " + line
            print "TO: " + targ_file
            print "======================"
            targ_dir = self.strip_file_from_path(targ_file)
            self.handle_directory(targ_dir)

    def handle_directory(self, dir):
        if dir not in self.created_dirs:
            print "CREATING: " + dir
            self.created_dirs.append(dir)
            self.create_directory(dir)
        else:
            print "EXISTS: " + dir

    def src_file_to_dest_file(self, filepath):
        '''
        strip  a number of chars form the beginning equal to the length of the
        src directory

        tack on a leading slash, then the dst directory, then another slash
        just in case, the the stripped path

        this may mean we have extra slashes like "/file//to/a/path" but the
        filter and join lines clean those up

        '''
        stripped = filepath[len(self.source):]
        prepended = "/" + self.destination + "/" + stripped
        parts = prepended.split('/')
        parts = filter(None, parts)
        return "/" + "/".join(parts)

    def strip_file_from_path(self, filepath):
        parts = filepath.split('/')
        parts.pop()
        parts = filter(None, parts)
        return "/" + "/".join(parts)

    def create_directory(self, dir):
        proc = Popen(['mkdir',
                      '-p',
                      dir],
                     stdout=PIPE)
        output, errors = proc.communicate()
        if proc.returncode or errors:
            print [proc.returncode, errors, output]
            exit

    def move_file(self, src, dst):
        proc = Popen(['mv',
                      src,
                      dst],
                     stdout=PIPE)
        output, errors = proc.communicate()
        if proc.returncode or errors:
            print [proc.returncode, errors, output]
            exit


if __name__ == "__main__":
    gg = RRDTree()
    gg.find_files()
    gg.handle_files()
