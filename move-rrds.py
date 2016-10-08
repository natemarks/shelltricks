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
        self.destination = "/tmp"
        self.age = 365
        self.subdirs = []
        self.__dict__.update(kwargs)
        print self.source
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

    def make_destination_tree(self):
        self.dest_dirs = []
        if self.source_files == []:
            self.source_files = ['/opt/zenoss/aaa/bbb/ccc/filename.txt']
        for line in self.source_files:
            targ_file = self.src_file_to_dest_file(line)
            print "======================"
            print "MOVING: " + line
            print "TO: " + targ_file
            print "======================"
            targ_dir = self.strip_file_from_path(targ_file)
            if targ_dir not in self.dest_dirs:
                print "CREATING: " + targ_dir
                self.dest_dirs.append(targ_dir)

        print self.prepend_dest_prefix()

    def strip_source_prefix(self):
        '''
        need to remvoe the source directory from every entry
        knowing how find works, we assume that every list entry begins with the
        self.source string so we remove an equal number of characters from the
        beginning of each entry
        '''
        dest_list = []
        if self.source_files == []:
            self.source_files = ['/opt/zenoss/aaa/bbb/ccc/filename.txt']
        for line in self.source_files:
            dest_list.append(line[len(self.source):])
        # remove duplicates by converting to set and back to list
        dest_list = list(set(dest_list))
        return dest_list

    def prepend_dest_prefix(self):
        '''
        prepend the new target directory onto every  path
        '''
        prepended_list = []
        for line in self.strip_source_prefix():
            line = "/" + self.destination + "/" + line
            parts = line.split('/')
#            filter out empty list elements
            parts = filter(None, parts)
            prepended_list.append("/" + "/".join(parts))
        return prepended_list

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


if __name__ == "__main__":
    gg = RRDTree()
    gg.create_directory("/tmpg/aaa/bbb/ccc")
