'''
TODO:  handle subtree  input
provided the following information:
 - file matching criteria
 - a source root directory
 - [optional source target subdirectory
 - destination root directory

Do the following:
mode: REPORT
report on all the matching files in the source target subdirectory if it's
provided, or the source root directory if not report

report displays:
    - matching criteria (fs object type: file, staleness, endswith string,
      source root, source subdir, destination root)
    - source file and destination file dictionary ()
    - aggregate file size
    - matching file count
report also creates a playback file which is a yaml object of the purge class
that can be used to reverse the actions
'''

from subprocess import PIPE, Popen
import os


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
        REPORT mode reports on the found files and saves the object to YAML
        COPY mode copies files to new location and saves the object to YAML
        MOVE mode moves them to the new location and saves the object to YAML
        ROLLBACK mode uses a object yaml file to rollback the changes of a MOVE
        '''
        # store all kwargs into the __dict__
        self.set_datestamp()
        self.source = "/opt/zenoss"
        self.destination = "/tmp/moved_rrds"
        self.file_extension = ".rrd"
        self.verbose = False
        self.file_dict = []
        self.created_dirs = []
        self.mode = "REPORT"
        self.__dict__.update(kwargs)
        self.age = "YEAR"
        self.gather_data()
        self.handle_files()
        self.write_object()
        self.print_report()

    def src_file_to_dest_file(self, filepath):
        '''
        prepend self.destination to the self.source value
        use os.path.sep to figure out if we're using \ /  or some other
        character to separate directories

        '''
        sep = os.path.sep
        orig_path_parts = filepath.split(sep)
        prepend_path_parts = self.destination.split(sep)
        prepend_path_parts.extend(orig_path_parts)
        parts = filter(None, prepend_path_parts)
        return sep + sep.join(parts)

    def get_dir_from_filepath(self, filepath):
        sep = os.path.sep
        parts = filepath.split(sep)
        parts.pop()
        parts = filter(None, parts)
        return sep + sep.join(parts)

    def validate_path(self, filepath):
        '''
        given a path to a file, use self.destination prepended to the file path
        to make sure that the path to the new file location exists

        *********
        TODO:  try this gather out instead of fild fils
        '''
        if os.path.isdir(self.get_dir_from_filepath(filepath)):
            proc = Popen(['mkdir',
                          '-p',
                          dir],
                         stdout=PIPE)
            output, errors = proc.communicate()
            if proc.returncode or errors:
                print [proc.returncode, errors, output]
                exit

    def gather_data(self):
        '''
        put the matching files  and their destinations into self.file_dict
        '''
        match_dict = {}
        for root, directories, filenames in os.walk(self.source):
            for filename in filenames:
                fullpath = os.path.join(root, filename)
                if filename.endswith(self.file_extension):
                    if self.file_older_than_n(fullpath,
                                              self.TIMEUNITS[self.age]):
                        match_dict[fullpath] = \
                            self.src_file_to_dest_file(fullpath)
        self.file_dict = match_dict

    def set_datestamp(self):
        import datetime
        now = datetime.datetime.now()
        format = "%Y-%m-%d-%H-%M-%S"
        self.timestamp = now.strftime(format)

    def write_object(self):
        import yaml
        filename = '-'.join([self.timestamp, 'RRDTree.yml'])
        with open(filename, 'w') as outfile:
                yaml.dump(self, outfile, default_flow_style=True)

    def convert_size(self, size):
        '''
        given a number in KB, convert it to other format
        '''
        import math
        if (size == 0):
            return '0B'
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size/p, 2)
        return '%s %s' % (s, size_name[i])

    def file_size_summary(self):
        '''
        look at the list of files and retunr the summ
        '''
        from os.path import getsize
        total_size = 0
        for file, dest in self.file_dict.iteritems():
            total_size = total_size + int(getsize(file))
        print "TOTAL SIZE: " + self.convert_size(total_size)

    def print_report(self):
        print "LOOKING AT FILES OLDER THAN ONE " + self.age
        print "THAT END WITH: " + self.file_extension
        print "SOURCE DIRECTORY: " + self.source
        print "DESTINATION DIRECTORY: " + self.destination
        print "NUMBER OF MATCHING FILES: " + str(len(self.file_dict))
        self.file_size_summary()
        if self.verbose:
            for key, val in self.file_dict.iteritems():
                print "##################"
                print "SOURCE: " + key
                print "DEST: " + val
                print "##################"

    def file_older_than_n(self, file, seconds):
        '''
        return true if the file is older than n seconds
        '''
        import time
        import os
        stat = os.stat(file)
        mtime = int(stat.st_mtime)
        return mtime < int(time.time()) - seconds

    def handle_files(self):
        for key, val in self.file_dict.iteritems():
            self.validate_path(val)
            if self.mode == "COPY":
                self.copy_file(key, val)
            elif self.mode == "MOVE":
                self.move_file(key, val)

    def copy_file(self, src, dst):
        proc = Popen(['cp',
                      src,
                      dst],
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

    def handle_directory(self, dir):
        if dir not in self.created_dirs:
            print "CREATING: " + dir
            self.created_dirs.append(dir)
            self.create_directory(dir)
        else:
            print "EXISTS: " + dir

    def do_rollback(self):
        if self.mode != "MOVE":
            print "fiels were not moved.  exiting"
            exit
        for key, val in self.file_dict.iteritems():
            self.validate_path(key)
            self.move_file(val, key)


if __name__ == "__main__":
    dscr = """
purge-tree is used to clean certain types of files out of a directory tree.
When run without any arguments, it reports the number and size of the mathcing
files in the source tree.
    """
    import argparse
    parser = argparse.ArgumentParser(description=dscr)
    parser.add_argument('--rollback', action='store', dest='rollback',
                        default='BADFILEPATH',
                        help='full path to the rollback file')
    parser.add_argument('--mode', action='store', dest='mode',
                        default='REPORT',
                        help='mode can be REPORT, COPY or MOVE',
                        choices=("REPORT", "COPY", "MOVE", "ROLLBACK"))
    parser.add_argument('--verbose', action='store_true', dest='verbose',
                        default=False,
                        help='print detailed report')
    parser.add_argument('--age', action='store', dest='age',
                        default='YEAR',
                        help='select files older than this many days')
    opts = parser.parse_args()

    if opts.mode == "ROLLBACK":
        import yaml
        with open(opts.rollback, 'r') as objfile:
            print "using rollback file " + opts.rollback
            gg = yaml.load(objfile)
            gg.do_rollback()

    else:
        gg = RRDTree(mode=opts.mode, verbose=opts.verbose, age=opts.age)
