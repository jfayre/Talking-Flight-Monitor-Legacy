from distutils.core import setup
import py2exe
import glob
import os
import babel
def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())

data=find_data_files('locale-data','locale-data',[
    '*'
    ])
py2exe_options = {'includes': ['pyttsx.drivers.sapi5', 'win32com.gen_py.C866CA3A-32F7-11D2-9602-00C04F8EE628x0x5x4'],
                   'typelibs': [('{C866CA3A-32F7-11D2-9602-00C04F8EE628}', 0, 5, 4)] }

setup(console=['flightFollowing.py'], options = {'py2exe': py2exe_options}, data_files=data)