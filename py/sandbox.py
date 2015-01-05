#!/usr/bin/env python2.7
from __future__ import print_function
from contextlib import contextmanager
import os, sys, random, json, commands

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
        raise Exception('%s <- system(%s)' %(status, cmd))
def PipeRead(cmd):
    print(cmd)
    status, out = commands.getstatusoutput(cmd)
    if status:
        raise Exception('%s <- `%s`' %(status, cmd))
    return out
def SvnCreate(dire):
    System('svnadmin create --fs-type fsfs %s' %dire)
    return 'file://' + os.path.abspath(dire)
def GitInit(dire):
    with mkdir(dire):
        System('git init')
    return os.path.abspath(dire)
class WithCD(object):
    """Decorate all methods of another object to
    change directory first.
    NOT CURRENTLY USED.
    http://stackoverflow.com/questions/6704151/python-equivalent-of-rubys-method-missing
    """
    def __init__(self, dire):
        self.dire = dire

class GitOne(object):
    """These methods should be called from the 'gitdire',
    as some paths are relative to that.
    """
    def __init__(self, gitdire, name, svnrepo):
        self.gitdire = gitdire
        self.name = name
        self.svnrepo = svnrepo
    def GetCacheDire(self):
        """Relative to GSD.
        """
        return os.path.join(gsd, self.svnname)
    def Subvert(self, path):
        dirname = self.svndire
        dirpath = dirname # TODO: might be in sub-dir
        mkdir(dirpath)
        svndirpath = os.path.join(gsd, dirname)
        mkdir(svndirpath)
        svnreldirpath = svndirpath # TODO: might need ../../....
        System('ln -sfn %s %s' %(svnreldirpath, dirname))
        with cd(svndirpath):
            System('svn add %s' %dirtree)
            System('svn commit -m added')
    def RefreshLink(self, link):
        with mkdir(gsd):
            name = self.name
            path = os.readlink(link)
            svndb = self.svndb
            #System('svn checkout file://%s %s' %(svndb, name))
            System('svn export %s/%s %s/%s' %(svnrepo, path, name, path))
    def Refresh(self, path, repo):
        """Assume in base of git-work-dir.
        """
        links = self.GetSymlinks()
        for link in links:
            self.RefreshLink(link)
        with cd(os.path.dirname(path)):
            svnrelpath = os.readlink(path)
            if not os.path.exists(svnrelpath):
                # Get part after .git/some.
                svnpath = svnrelpath # HUH?
                cmd = 'svn export %s%s' %(self.repo, svnpath)
                with cd(os.path.dirname(svnrelpath)):
                    pass # export?
            assert os.path.exists(svnrelpath)
        assert os.path.exists(path)
    def Relink(self, path, rev, repo):
        # Modify symlink, then ...
        self._Refresh(path, repo)
class GitSome(object):
    def __init__(self, gitdire, svndirmap):
        self.gitdire = gitdire
        self.svndbdirmap = svndirmap
        self.svndefault = svndirmap.keys()[0]
    def Reconstruct(self, path, repo=None):
        '''Remove symlink (if any).
        Copy linked dir-tree from repo to where path was.
        This allows you to forget about git-some for this dirlink.
        You probably want to Unlock first.
        '''
    def Subvert(self, path, repo=None):
        '''Move path-tree (relative to git-dir) into repo (under .git/some/repo/rev/).
        Add it to repo and commit.
        Then create symlink from path.
        '''
        if repo is None: repo = self.svndefault
        with cd(self.gitdire):
            return self._Link(path, repo)
    def Refresh(self, path, rev, repo=None):
        '''Re-create symlink.
        Maybe revision changed. Or maybe we have directory-versions.
        '''
        if repo is None: repo = self.svndefault
        with cd(gs.gitdire):
            return self._Relink(path, repo)
    def Relink(self, path, rev, repo=None):
        '''Re-create symlink.
        Maybe revision changed. Or maybe we have directory-versions.
        '''
        if repo is None: repo = self.svndefault
        with cd(gs.gitdire):
            return self._Relink(path, repo)
    def Commit(self, path, repo=None):
        '''Commit within repo.
        Then move the repo to its new revision-number, and symlink it.
        Then 'git add' the new symlink.
        '''
    def Unlock(self, path, repo=None):
        '''Make path in repo (under .git/some) writable.
        '''
    def Lock(self, path, repo=None):
        '''Make path in repo (under .git/some) read-only.
        '''
def RmDir(dire):
    dire = os.path.abspath(dire)
    if os.path.exists(dire):
        cmd = 'rm -rf %s' %dire
        msg = cmd + '?'
        print(msg)
        yes = raw_input()
        if yes and yes[0] == 'n':
            raise Exception(msg + yes)
        System(cmd)
def CreateSandbox(dire, proj):
    RmDir(dire)
    with mkdir(dire):
        svndb = SvnCreate('binaries-proj')
        gitwd = GitInit(os.path.join(dire, proj))
        print(svndb, gitwd)
    rev = GetSvnInfoRevision(PopulateSvn(os.path.join(svndb, 'base'), 'base'))
    with cd(os.path.join(gitwd)):
        os.symlink('.git/some/svn1/base', 'base')
        meta = {'links': {
            'base': 'svn1/r%d/base'%rev,
            },
        }
        with open('.git-some', 'w') as f:
            f.write(json.dumps(meta))
    return svndb, gitwd
def PopulateTree(dirtree, n, size):
    with mkdir(dirtree):
        WriteRands(n, size)
def PopulateSvn(svnpath, dirtree):
    """Can be rel to CWD.
    Ex. PopulateSvn('file://foo-svn/base', 'base')
    return svn info
    """
    PopulateTree(dirtree, 1, 3)
    # Import the contents of 'dirtree' into 'svnpath'.
    # If you want the basename of in svn, append it to svnpath.
    cmd = "svn import -m 'PopulateSvn()' %s %s" %(dirtree, svnpath)
    System(cmd)
    RmDir(dirtree)
    info = PipeRead("svn info %s" %svnpath)
    return info
def GetSvnInfoRevision(info):
    print(info)
    print(list(line.split(':', 1) for line in info.split('\n')))
    print(list(list(s.strip() for s in line.split(':', 1)) for line in
            info.split('\n') if line.strip()))
    infod = dict((s.strip() for s in line.split(':', 1)) for line in
            info.split('\n') if line.strip())
    return int(infod['Revision'])
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
def RandFilename(base='foo-%000d', r=10):
    return base%random.randrange(r)
def WriteRand(filename, size):
    '''into cwd'''
    print('Write %d bytes into %r' %(size, filename))
    with open(filename, 'wb') as f:
        f.write(b'x'*size)
def WriteRands(n, size):
    '''into cwd'''
    for i in range(n):
        filename = RandFilename('foo-%000d', 10)
        WriteRand(filename, size)
def Play(gs):
    with cd(gs.gitdire):
        path = ''
        gs.Refresh(path)  # Ensure symlink points somewhere.
        return
        path = 'bin'
        with mkdir(path):
            WriteRands(1, 1)
        #gs.Subvert(path)  # Move path into .git; Revise; overwrite; Commit.
        path = ''
        gs.Refresh(path)  # Ensure symlink points somewhere.
        #gs.Relink(path, 'r2')  # Modify symlink and Refresh.
        #gs.Revise(path)  # Symlink a checked-out repo.
        #WriteRand(os.path.join(path, RandFilename()))
        #gs.Commit(path)  # Commit the sandbox, then Relink to latest revision.
        #gs.Reconstruct(path)  # Undo all.
def Main(prog, dire, proj):
    svnrepo, gitwd = CreateSandbox(dire, proj)
    gs = GitOne(gitwd, 'svn1', svnrepo)
    #Play(gs)
    #AddRand(gs, 1)
if __name__=="__main__":
    Main(*sys.argv)
