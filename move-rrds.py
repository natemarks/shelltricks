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
        self.find_output = proc.communicate()[0].split()

    def make_destination_tree(self):
        print self.prepend_dest_prefix()

    def strip_source_prefix(self):
        '''
        need to remvoe the source directory from every entry
        knowing how find works, we assume that every list entry begins with the
        self.source string so we remove an equal number of characters from the
        beginning of each entry
        '''
        dest_list = []
        if self.find_output == []:
            self.find_output = ['/opt/zenoss/aaa/bbb/ccc/']
        for line in self.find_output:
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


if __name__ == "__main__":
    gg = RRDTree()
    gg.make_destination_tree()
