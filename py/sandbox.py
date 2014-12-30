#!/usr/bin/env python2.7
from __future__ import print_function
from contextlib import contextmanager
import os, sys

# git-some dir:
gsd = os.path.join('.git', 'some')

_dirstack = list('.')

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    #_dirstack.push(prevdir)
    os.chdir(newdir)
    print(' In: %r' %os.path.abspath(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        print(' To: %r' %os.path.abspath(prevdir))
@contextmanager
def mkdir(dire, mode=0755):
    if not os.path.isdir(dire):
        os.makedirs(dire, mode)
    with cd(dire):
        yield
def System(cmd):
    print(cmd)
    status = os.system(cmd)
    if status:
        raise Exception('%s <- `%s`' %(status, cmd))
def SvnCreate(dire):
    System('svnadmin create --fs-type fsfs %s' %dire)
    return os.path.abspath(dire)
def Sandbox(dire, proj):
    if os.path.exists(dire):
        cmd = 'rm -rf %s' %dire
        msg = cmd + '?'
        print(msg)
        yes = raw_input()
        if yes and yes[0] == 'n':
            raise Exception(msg + yes)
        System(cmd)
    with mkdir(dire):
        svndb = SvnCreate('binaries-proj')
        with mkdir(proj):
            System('git init')
            with mkdir(gsd):
                System('svn checkout file://%s .' %svndb)
def Main(prog, dire, proj):
    Sandbox(dire, proj)
if __name__=="__main__":
    Main(*sys.argv)
