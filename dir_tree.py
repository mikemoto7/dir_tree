#!/usr/bin/env python

"""
Description:
Similar to the Linux find(1) command.
Recursively goes through a directory tree and displays the names of files and subdirs found.

Runstring:
%(scriptName)s [options] .   # start search from current directory
%(scriptName)s [options] dir1,dir2,dir3

Choose options:

Files:
--filename_mask regex_string = Only search for filenames containing this regular-expression string.
--size = Show filesize in bytes for each file found.
--mtime = Show file mod time for each file found.  Format:  YYYYMMDDHHMM
--link = Show whether the file is a symlink or not.
The order that --size, --mtime, and --link appear in the dir_tree.py runstring or in the dir_tree() function args param will determine the sequence of how they are output by dir_tree.
--count_sorted_by_count = Show count of files in each directory, list sorted by file count.
--count_sorted_by_dirname = Show count of files in each directory, list sorted by dir name.

Dirs:
--dirs = Show names of dirs instead of files.
--count_sorted_by_dir_tree [level] = Show count of files in each directory and each subtree.  You can specify an optional level ID number to see particular levels and above only.  For example, level 1 will display the top level of subdir trees, level 2 will display the top 2 levels, etc.  File counts will still be for all displayed and not displayed dir trees.  If level is not specified, default is to show all levels.

Misc:
--oi = Show output immediately.  Don't create a list.
--fo dir_basename1[|dir_basename2|...] = Directories to filter out and not walk.
--fo default = Using default dirs to filter out:  " + fo_default)

If the output requested contains multiple fields per line, the field_separator_char " + field_separator_char + " will be used to separate the fields.

Module Use:
The dir_tree function allows you to specify your own function to run for each file found.  IMPORTANT:  Your func param and your function's params must show up last in the dir_tree param list.  Example call:

   dir_tree(start_dir='.', filename_mask='.py', func=example_func, param1=56, param2='hello')

Search for "example_func" code further down.

--func_keyword_param_example = Will show you an example func call using keyworded params.


Monitor mode for debugging:

If you have a lot of files to traverse through but infrequent output, you may not see any screen output for several minutes.  Use the following to see what files are currently being processed:

<ctrl-c> = Monitor mode:  Toggle displaying the names of all files found.  These monitor-mode filenames will have a '#' in front of them to distinguish them from filenames you want deliberately displayed by your scripts which use dir_tree().  Example of Monitor mode output:

# /cygdrive/c/$RECYCLE.BIN/S-1-5-21-1870694582-2382554345-2085229990-1000/$RBE7IJK.3/setuptools/command/sdist.pyc
# /cygdrive/c/$RECYCLE.BIN/S-1-5-21-1870694582-2382554345-2085229990-1000/$RBE7IJK.3/setuptools/command/setopt.py
# /cygdrive/c/$RECYCLE.BIN/S-1-5-21-1870694582-2382554345-2085229990-1000/$RBE7IJK.3/setuptools/command/setopt.pyc
# /cygdrive/c/$RECYCLE.BIN/S-1-5-21-1870694582-2382554345-2085229990-1000/$RBE7IJK.3/setuptools/command/setopt.pyc
/cygdrive/c/$RECYCLE.BIN/S-1-5-21-1870694582-2382554345-2085229990-1000/$RBE7IJK.3/setuptools/command/setzzz.py
# /cygdrive/c/$RECYCLE.BIN/S-1-5-21-1870694582-2382554345-2085229990-1000/$RBE7IJK.3/setuptools/command/test.py

Your script is using dir_tree() to look for setzzz.py.

"""

import os, sys, re
import getopt
import time

scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
libDir = scriptDir + '/lib'

sys.path.append(scriptDir)
sys.path.append(libDir)

scriptName = os.path.basename(__file__).replace('.pyc', '.py')

import signal

display_all_filenames = False  # To check whether the script is still alive processing a large dir tree.

def handler(signum, frame):
    from logging_wrappers import user_input
    global display_all_filenames
    global stop_flag

    print('Signal handler called with signal', signum)
    while True:
        answer = user_input("Quit? (y/n) ").strip()
        # print("answer = '" + answer + "'")
        if answer == 'y':
            stop_flag = True
            print("Please wait...")
            sys.exit(0)
        elif answer != 'n':
            continue
        break
    while True:
        answer = user_input("Toggle filename trace output? (y/n) ")
        if answer == 'y':
            display_all_filenames = not display_all_filenames
            break
        elif answer != 'n':
            continue
        break


signal_num = signal.SIGINT
signalName = "SIGINT"

#===================================================

def func_wrapper(fullfilename, func, **args):
    # print(44, fullfilename, func, args)
    rc, result = func(fullfilename, **args)
    return rc, result

# Your function must have these input params with these names in this order.
def example_func(fullfilename, **args):
   for key in args:
      print(fullfilename, "{0} = {1}".format(key, args[key]))
   # print("example_func:", param1, param2)
   return 0, "success"  # return required

stop_flag = False

field_separator_char = '%'

def dir_tree(start_dir='.', filename_mask = '', object_type = 'file', filter_out_dirs='', output_mode='', func=None, **args):
    # global fd

    signal.signal(signal_num, handler)

    # print 47, args
    # print "start_dir = " + start_dir
    ignore_dir = ''
    return_list = []
    for dirName, subdirList, fileList in os.walk(start_dir):
        if stop_flag == True:
            sys.exit(1)
        # print "loop: " + dirName + "," + str(subdirList) + "," + str(fileList)
        if filter_out_dirs != '':
            # if re.search("not_used_anymore|\.git|\.svn|bash2py|7\.0|6\.2\.0", dirName):
            # if re.search("not_used_anymore|\.git|\.svn|bash2py", dirName):
            if re.search(filter_out_dirs, dirName):
                if ignore_dir == '':
                    ignore_dir = dirName
                    continue
                if re.search('^' + ignore_dir, dirName):
                    continue
                print(("# Ignoring: " + dirName))
                ignore_dir = dirName
                continue
        if object_type == 'dir':
            result = []
            if func != None:
                rc, result = func(dirName, subdirList, fileList)
                if rc == 0:
                    if output_mode == 'oi':
                        print((dirName + ',' + str(result)))
                    else:
                        if len(result) != 0:
                            return_list = result
            else:
                return_list.append(dirName)
            continue
        # print('%s/%s' % (dirName, fname))
        # print('Found directory: %s' % dirName)
        for fname in fileList:
            if display_all_filenames == True:  # To check whether the script is still alive processing a large dir tree.
                print("# " + dirName + "/" + fname)
            if filename_mask == '':
                fullfilename = dirName + '/' + fname
                result = ''
                if func != None:
                    rc, result = func_wrapper(fullfilename, func, **args)
                    if rc == 0:
                        if output_mode == 'oi':
                            print(fullfilename + field_separator_char + result)
                        else:
                            return_list.append(fullfilename + field_separator_char + result)
                else:
                    if output_mode == 'oi':
                        print(fullfilename)
                    else:
                        return_list.append(fullfilename)
                continue
            # if re.search("\.py$", fname):
                # full_fname = "%s/%s" % (dirName, fname)
                # fd.write(full_fname + "\n")
                # print dirName + "/" + fname
                # return_list.append('%s/%s' % (dirName, fname))
                # continue
            if re.search(filename_mask, fname):
                fullfilename = dirName + '/' + fname
                result = ''
                if func != None:
                    # print(102, fullfilename, func, args)
                    # rc, result = func(fullfilename, args)
                    rc, result = func_wrapper(fullfilename, func, **args)
                    if rc == 0:
                        if output_mode == 'oi':
                            print(fullfilename + ',' + result)
                        else:
                            if result != '':
                                return_list.append(result)
                else:
                    if output_mode == 'oi':
                        print(fullfilename)
                    else:
                        return_list.append(fullfilename)
                continue
                # print('%s/%s' % (dirName, fname))
                # cmd = ("ls -l %s/%s" % (dirName, fname))
                # rc, output = run_local_command(cmd)
                # if rc != 0:
                #    print("ERROR: cmd: " + cmd)
                #    print("output: " + output)
                #    continue
                # print(output)
                # return_list.append(output)
        # Remove the first entry in the list of sub-directories
        # if there are any sub-directories present
        # if len(subdirList) > 0:
        #     del subdirList[0]

        # for subdir in subdirList:
        #    # print "dirName/subdir = " + dirName+"/"+subdir
        #    rc, entries = dir_tree(dirName+"/"+subdir)
        #    return_list += entries

    return 0,return_list

#------------------------------

'''
def getfilesize(fullpath, args = []):
   if os.path.isfile(fullpath):
      result = os.path.getsize(fullpath)
      return 0, str(result)
   else:
      return 1, "not_a_file"

#------------------------------

def getfileModTime(fullpath, args = []):
   if os.path.isfile(fullpath):
      result = os.path.getmtime(fullpath)
      return 0, str(result)
   else:
      return 1, "not_a_file"
'''

#------------------------------

def getfileinfo(fullpath, getfileinfo_args = []):
    if not os.path.isfile(fullpath):
        return 1, "not_a_file"

    result = ''
    separator = ''
    for arg in getfileinfo_args:
        if arg == '--mtime':
            result += separator + time.strftime('%Y%m%d%H%M', time.gmtime(os.path.getmtime(fullpath)))
            separator = field_separator_char
            continue
        if arg == '--size':
            result += separator + str(os.path.getsize(fullpath))
            separator = field_separator_char
            continue
        if arg == '--link':
            if os.path.islink(fullpath):
                result += separator + 'symlink:' + os.readlink(fullpath)
            else:
                result += separator + 'regular_file'
            separator = field_separator_char
            continue

        print("ERROR: Unrecognized getfileinfo option = " + arg)
        sys.exit(1)

    return 0, str(result)

#------------------------------

last_fullpath = ''
filecount = 0

def getfilecount(fullpath, args = []):
    global last_fullpath
    global filecount

    if os.path.isfile(fullpath):
        return_string = ''
        result = os.path.dirname(fullpath)
        if last_fullpath == '':
            last_fullpath = result
            filecount += 1
        elif result == last_fullpath:
            filecount += 1
        else:
            # print str(filecount) + ":" + last_fullpath
            return_string = str(filecount) + ":" + last_fullpath
            last_fullpath = result
            filecount = 1

        return 0, return_string
    else:
        return 1, "not_a_file"

#------------------------------

# Recursive function

level_wanted = -1
curr_level = -1
dir_paths = []
output_list = []

def getfilecount_tree(dirName):
    global curr_level
    global level_wanted
    global dir_paths


    # print "Entering getfilecount_tree: dirName = " + dirName

    curr_level += 1
    local_subdirs = []
    local_filecount = 0
    tree_filecount  = 0
    for filename in os.listdir(dirName):
        path = os.path.join(dirName, filename)
        if os.path.isdir(path):
            local_subdirs.append(path)
        else:
            local_filecount += 1
    tree_filecount = local_filecount
    for subdir in local_subdirs:
        rc, subdir_local_filecount, subdir_tree_filecount = getfilecount_tree(subdir)
        tree_filecount += subdir_tree_filecount
        # print subdir + "," + str(subdir_local_filecount) + "," + str(subdir_tree_filecount)

    # print 'debug: ' + dirName + ', curr_level ' + str(curr_level) + ', level_wanted ' + str(level_wanted) + ', local_filecount ' + str(local_filecount) + ', tree_filecount ' + str(tree_filecount)
    if (level_wanted == -1) or (level_wanted != -1 and curr_level <= level_wanted):
        dir_paths.append(str(curr_level) + ":" + dirName + "," + str(local_filecount) + "," + str(tree_filecount))
    curr_level -= 1

    if curr_level == 0:
        dir_paths.reverse()
        for path in dir_paths:
            # print path
            output_list.append(path)
        dir_paths = []

    if curr_level == -1:
        # print dir_paths[:-1]
        # print len(dir_paths)
        print(dir_paths[0])
        total = 0
        for path in output_list:
            print(path)
            total += int(path.split(',')[2])
        print("debug: second-check final subdir filecount total = " + str(total) + " + top-level filecount = " + dir_paths[0].split(',')[1])

    return 0, local_filecount, tree_filecount

#------------------------------

fo_default = 'not_used_anymore|\.git|\.svn|bash2py'

def usage():
    print(__doc__ % {'scriptName': scriptName, 'signalName': signalName,})
    sys.exit(1)

#===================================================

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()

    output_mode = ''
    getfileinfo_args = []
    filter_out = ''
    get_file_count_sorted_by_count_flag = False
    get_file_count_sorted_by_dirname_flag = False
    show_dirs = False
    get_file_count_sorted_by_dir_tree_flag = False
    filename_mask = ''
    func_keyword_param_example = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["size", "mtime", "link", "count_sorted_by_count", "count_sorted_by_dirname", "show_dirs", "count_sorted_by_dir_tree=", "oi", "filename_mask=", "func_keyword_param_example"])
    except:
        print("ERROR: Unrecognized runstring option.")
        usage()

    for opt, arg in opts:
        if opt == "--size":
            getfileinfo_args.append(opt)
        elif opt == "--mtime":
            getfileinfo_args.append(opt)
        elif opt == "--link":
            getfileinfo_args.append(opt)
        elif opt == "--count_sorted_by_count":
            get_file_count_sorted_by_count_flag = True
        elif opt == "--count_sorted_by_dirname":
            get_file_count_sorted_by_dirname_flag = True
        elif opt == "--count_sorted_by_dir_tree":
            get_file_count_sorted_by_dir_tree_flag = True
            try:
                level_wanted = int(arg)
            except:
                level_wanted = -1
        elif opt == "--show_dirs":
            show_dirs = True
        elif opt == "--oi":
            output_mode = 'oi'
        elif opt == "--filename_mask":
            filename_mask = arg
        elif opt == "--func_keyword_param_example":
            func_keyword_param_example = True
        elif opt == "--fo":
            if arg == 'default':
                filter_out = fo_default
            else:
                filter_out = arg
        else:
            usage()

    # listFile = scriptName + "_list.txt"
    # fd = open(listFile, "w")

    if len(args) == 0:
        print("ERROR: Missing starting directory name(s).")
        usage()

    for start_dir in sys.argv[-1].split(','):
        # print("start_dir: " + start_dir)
        # rc, filelist = dir_tree(start_dir=start_dir, "\.py$")

        if func_keyword_param_example == True:
            rc, filelist = dir_tree(start_dir=start_dir, filename_mask=filename_mask, filter_out_dirs = filter_out, output_mode = output_mode, func=example_func, param1=56, param2='hello')
            print("Either output results per file in example_func, or here after all files have been processed.")
            # for file_entry in filelist:
            #     print(file_entry)

        elif len(getfileinfo_args) > 0:
            # If user requests both size and modtime info, maintain sequence.
            rc, filelist = dir_tree(start_dir=start_dir, filename_mask=filename_mask, func = getfileinfo, args=getfileinfo_args, filter_out_dirs = filter_out, output_mode = output_mode)
            for file_entry in filelist:
                # print file_entry[0] + ',' + file_entry[1]
                print(file_entry)

        elif get_file_count_sorted_by_count_flag or get_file_count_sorted_by_dirname_flag:
            rc, filelist = dir_tree(start_dir=start_dir, filename_mask=filename_mask, func = getfilecount, filter_out_dirs = filter_out, output_mode = output_mode)
            # filelist.sort(key=int)
            # print sorted(format_data, key=lambda x: (int(x[1].split(None, 1)[0]) if x[1][:1].isdigit() else 999, x))         print "ERROR: Runstring options."
            if get_file_count_sorted_by_count_flag == True:
                filelist.sort(key=lambda x: (int(x.split(':')[0])))
            for file_entry in filelist:
                print(file_entry)
        elif get_file_count_sorted_by_dir_tree_flag:
            getfilecount_tree(start_dir)
            # for line in filecount_list:
            #    print str(line)
        elif show_dirs:
            rc, dirlist = dir_tree(start_dir=start_dir, filename_mask=filename_mask, object_type = 'dir', filter_out_dirs = filter_out, output_mode = output_mode)
            for dir_entry in dirlist:
                print(dir_entry)
        else:
            rc, filelist = dir_tree(start_dir=start_dir, filename_mask=filename_mask, filter_out_dirs = filter_out, output_mode = output_mode)
            for file_entry in filelist:
                print(file_entry)

        # rc = dir_tree(start_dir)
        #    if re.search("\.py$", fname):
        #       cmd = ("ls -l %s" % (fname))
        #       rc, output = run_local_command(cmd)
        #       if rc != 0:
        #           print("ERROR: cmd: " + cmd)
        #           print("output: " + output)
        #           continue
        #       fd.write(output + "\n")

    # fd.close()



