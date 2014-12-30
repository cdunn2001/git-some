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
    def Unlink(self, path, repo=None):
        '''Remove symlink (if any).
        Copy linked dir-tree from repo to where path was.
        This allows you to forget about git-some for this dirlink.
        You probably want to Unlock first.
        '''
    def Link(self, path, repo=None):
        '''Move path-tree (relative to git-dir) into repo (under .git/some/repo/rev/).
        Add it to repo and commit.
        Then create symlink from path.
        '''
    def Unlock(self, path, repo=None):
        '''Make path in repo (under .git/some) writable.
        '''
    def Commit(self, path, repo=None):
        '''Commit within repo.
        Then move the repo to its new revision-number, and symlink it.
        Then 'git add' the new symlink.
        '''
    def Lock(self, path, repo=None):
        '''Make path in repo (under .git/some) read-only.
        '''
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
    with cd(gs.gitdire):
        dirname = gs.svndefault
        dirpath = dirname # TODO: might be in sub-dir
        mkdir(dirpath)
        svndirpath = os.path.join(gsd, dirname)
        mkdir(svndirpath)
        svnreldirpath = svndirpath # TODO: might need ../../....
        System('ln -sfn %s %s' %(svnreldirpath, dirname))
        filename = 'foo-%000d' %random.randrange(10)
        filepath = os.path.join(filename) # TODO: Allow files in sub-dirs of link-dir
        svnpath = os.path.join(svndirpath, filepath)
        print('Write %d bytes into %r' %(size, svnpath))
        with open(svnpath, 'w') as f:
            f.write(b'x'*size)
        with cd(svndirpath):
            System('svn add %s' %filepath)
            System('svn commit -m added')
def WriteRand(size):
    '''into cwd'''
    filename = 'foo-%000d' %random.randrange(10)
    print('Write %d bytes into %r' %(size, filename))
    with open(filename, 'w') as f:
        f.write(b'x'*size)
    return filename
def WriteRands(n, size):
    '''into cwd'''
    for i in range(n):
        WriteRand(size)
def Play(gs):
    with cd(gs.gitdire):
        path = 'bin'
        with mkdir(path):
            WriteRands(1, 1)
        gs.Link(path)
def Main(prog, dire, proj):
    gs = CreateSandbox(dire, proj)
    Play(gs)
    #AddRand(gs, 1)
if __name__=="__main__":
    Main(*sys.argv)
