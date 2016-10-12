'''
NOTE:  because I use argparse, this tool must be run on python 2.7 or above. on
a Z4 collector, that means running it at the zenoss user

clean-tree is used to clean certain types of files out of a directory tree.
When run without any arguments, it reports the number and size of the mathcing
files in the source tree.

self.source [default: '/opt/zenoss' ]:  is the directory scope of the find
command.  matching files will be acted upon

self.destination [default: '/tmp/moved_rrds' ]: the directories under the
target tree that contain matching files will be recreated in the destination
directory

self.age:  files older than <age> days will be included in the find

self.mode:
     - COPY : matching files in the source tree wil be copied to the
       destination tree
     - MOVE : matching files in the source tree will be moved to the
       destination tree
     - REPORT : report on the foudn files without chaning anything

'''


from subprocess import PIPE, Popen


class RRDTree(object):
    '''
    RRDTree object to be managed
    '''
    HOUR_IN_SECONDS = 3600
    DAY_IN_SECONDS = 86400
    YEAR_IN_SECONDS = 31536000
    TIMEUNITS = {'HOUR': 3600,
                 'DAY': 86400,
                 'YEAR': 31536000
                 }

    def __init__(self, *args, **kwargs):
        '''
        REPORT mode reports on the found files
        COPY mode copies files to new location
        MOVE mode moves them to the new location
        '''
        # store all kwargs into the __dict__
        self.source = "/opt/zenoss"
        self.destination = "/tmp/moved_rrds"
        self.file_extension = ".rrd"
        self.verbose = False
        self.source_files = []
        self.created_dirs = []
        self.mode = "REPORT"
        self.__dict__.update(kwargs)
        self.find_files()
        self.handle_files()
        self.print_report()
        self.age = "YEAR"

    def convert_size(self, size):
        import math
        if (size == 0):
            return '0B'
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size/p, 2)
        return '%s %s' % (s, size_name[i])

    def file_size_summary(self):
        from os.path import getsize
        total_size = 0
        for file in self.source_files:
            total_size = total_size + int(getsize(file))
        print "TOTAL SIZE: " + self.convert_size(total_size)

    def detailed_report(self):
        pass

    def print_report(self):
        print "LOOKING AT FILES OLDER THAN ONE " + self.age
        print "THAT END WITH: " + self.file_extension
        print "SOURCE DIRECTORY: " + self.source
        print "DESTINATION DIRECTORY: " + self.destination
        print "NUMBER OF MATCHING FILES: " + str(len(self.source_files))
        self.file_size_summary()

    def file_older_than_n(self, file, seconds):
        '''
        return true if the file is ilder than n seconds
        '''
        import time
        import os
        stat = os.stat(file)
        mtime = int(stat.st_mtime)
        return mtime < int(time.time()) - seconds

    def find_files(self):
        import os
        match_list = []
        for root, directories, filenames in os.walk(self.source):
            for filename in filenames:
                fullpath = os.path.join(root, filename)
                if filename.endswith(self.file_extension):
                    if self.file_older_than_n(fullpath,
                                              self.TIMEUNITS[self.age]):
                        match_list.append(fullpath)
        self.source_files = match_list

    def handle_files(self):
        if self.source_files == []:
            self.source_files = ['/opt/zenoss/aaa/bbb/ccc/first.txt',
                                 '/opt/zenoss/aaa/bbb/ccc/third.txt',
                                 '/opt/zenoss/ddd/eee/fff/second.txt']
        for line in self.source_files:
            targ_file = self.src_file_to_dest_file(line)
            targ_dir = self.strip_file_from_path(targ_file)
            self.handle_directory(targ_dir)
            if self.mode == "COPY":
                self.copy_file(line, targ_file)
            elif self.mode == "MOVE":
                self.move_file(line, targ_file)
            if self.verbose:
                print "SOURCE: " + line
                print "DEST: " + targ_file

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

    def copy_file(self, src, dst):
        print "======================"
        print "COPYING: " + src
        print "TO: " + dst
        print "======================"
        proc = Popen(['cp',
                      src,
                      dst],
                     stdout=PIPE)
        output, errors = proc.communicate()
        if proc.returncode or errors:
            print [proc.returncode, errors, output]
            exit

    def move_file(self, src, dst):
        print "======================"
        print "MOVING: " + src
        print "TO: " + dst
        print "======================"
        proc = Popen(['mv',
                      src,
                      dst],
                     stdout=PIPE)
        output, errors = proc.communicate()
        if proc.returncode or errors:
            print [proc.returncode, errors, output]
            exit


if __name__ == "__main__":
    dscr = """
clean-tree is used to clean certain types of files out of a directory tree.
When run without any arguments, it reports the number and size of the mathcing
files in the source tree.
    """
    import argparse
    parser = argparse.ArgumentParser(description=dscr)
    parser.add_argument('--mode', action='store', dest='mode',
                        default='REPORT',
                        help='mode can be REPORT, COPY or MOVE',
                        choices=("REPORT", "COPY", "MOVE"))
    parser.add_argument('--verbose', action='store_true', dest='verbose',
                        default=False,
                        help='print detailed report')
    parser.add_argument('--age', action='store', dest='age',
                        default='YEAR',
                        help='select files older than this many days')
    opts = parser.parse_args()

    gg = RRDTree(mode=opts.mode, verbose=opts.verbose, age=opts.age)
