#!/usr/bin/env python2.7
from __future__ import print_function
from contextlib import contextmanager
import os, sys, random

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
class GitSome(object):
    def __init__(self, gitdire, svndirmap):
        self.gitdire = gitdire
        self.svndbdirmap = svndirmap
        self.svndefault = svndirmap.keys()[0]
def CreateSandbox(dire, proj):
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
                svn1 = 'svn1'
                System('svn checkout file://%s %s' %(svndb, svn1))
    return GitSome(os.path.join(dire, proj), {'svn1': svndb})
def AddRand(gs, size):
    filename = 'foo-%000d' %random.randrange(10)
    svnpath = os.path.join(gs.gitdire, gsd, gs.svndefault, filename)
    print('Write %d bytes into %r' %(size, svnpath))
    with open(svnpath, 'w') as f:
        f.write(b'x'*size)
    #with cd(gs.
def AddRands(gs, n, size):
    for i in range(n):
        AddRand(gs, size)
def Main(prog, dire, proj):
    gs = CreateSandbox(dire, proj)
    AddRand(gs, 1)
if __name__=="__main__":
    Main(*sys.argv)
