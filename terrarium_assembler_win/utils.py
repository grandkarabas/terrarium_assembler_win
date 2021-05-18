"""
    Different (geeky) utils for TA
"""
import os
import subprocess
import shutil
import stat
import pathlib
from easydict import EasyDict as edict
# from jinja2 import Template, Undefined
from jinja2 import Environment, FileSystemLoader, Template, Undefined, DebugUndefined
# from elevate import elevate

def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    pass


def folder_size(path, *, follow_symlinks=False):
    '''
    Counting size of a folder. 
    '''
    try:
        if not os.path.exists(path):
            # Nonexistant folder has zero size.
            return 0
        it = list(os.scandir(path))
        # with os.scandir(path) as it:
        return sum(folder_size(entry, follow_symlinks=follow_symlinks) for entry in it)
    except NotADirectoryError:
        return os.stat(path, follow_symlinks=follow_symlinks).st_size

def wtf(f):
    '''
    For debugging purposes.
    '''
    for wtf_ in ['PYTEST', '/tests']:
        if wtf_ in f:
            return True
        
class NullUndefined(Undefined):
  def __getattr__(self, key):
    return ''        

def yaml_load(filename, vars_=None):
    '''
    Load yaml file into edict. Hide edict deps.
    ''' 
    import yaml

    fc = None
    # with open(filename, 'r') as f:
    dir_, filename_ = os.path.split(os.path.abspath(filename))
    file_loader = FileSystemLoader(dir_)
    env = Environment(loader=file_loader, undefined=DebugUndefined)
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.rstrip_blocks = True            

    template = env.get_template(filename_)

    real_yaml = ''
    try:
        for try_ in range(5):
            real_yaml = template.render(vars_)
            ld = yaml.safe_load(real_yaml)
            vars_ = {**vars_, **ld}

        # for key in vars_:
        #     if key.endswith('_dir'):
        #         vars_[key] = vars_[key].replace('/', '@')

        real_yaml = template.render(vars_)
        fc = edict(yaml.safe_load(template.render(vars_)))
    except Exception as ex_:
        print(f'Error parsing {filename_} see "troubles.yml" ')    
        with open("troubles.yml", 'w', encoding='utf-8') as lf:
            lf.write(real_yaml)
        raise ex_    
    # for key in fc:
    #     if key.endswith('_dir'):
    #         fc[key] = fc[key].replace('/', '\\')
    return fc



def rmdir(oldpath):
    if os.path.exists(oldpath):
        shutil.rmtree(oldpath, ignore_errors=True)
    if os.path.exists(oldpath):
        os.system('sudo rm -rf "%s"' % oldpath)
    #     elevate(graphical=False)
    #     shutil.rmtree(oldpath)
    pass

def git2dir(git_url, git_branch, path_to_dir):
    oldpath = path_to_dir + '.old'
    newpath = path_to_dir + '.new'
    rmdir(oldpath)
    pdir = os.path.split(path_to_dir)[0]
    os.chdir(pdir)
    scmd = 'git --git-dir=/dev/null clone --single-branch --branch %(git_branch)s  --depth=1 %(git_url)s %(newpath)s ' % vars()
    rmdir(newpath)
    os.system(scmd)
    if os.path.exists(newpath):
        if os.path.exists(path_to_dir):
            rmdir(oldpath)
            shutil.move(path_to_dir, oldpath)
        print(newpath, "->", path_to_dir)    
        shutil.move(newpath, path_to_dir)
    pass

def make_setup_if_not_exists():
    '''
    If python package without setup.py
    (for example Poetry)
    '''
    if not os.path.exists('setup.py') and os.path.exists('setup.cfg'):
        from poetry.masonry.builders.sdist import SdistBuilder
        from poetry.factory import Factory
        factory = Factory()
        poetry = factory.create_poetry('.')                
        sdist_builder = SdistBuilder(poetry, None, None)
        setuppy_blob = sdist_builder.build_setup()
        with open('setup.py', 'wb') as unit:
            unit.write(setuppy_blob)
            unit.write(b'\n# This setup.py was autogenerated using poetry.\n')                
    pass


def giturl2folder(git_url):
    _, fld_ = os.path.split(git_url)
    fld_, _ = os.path.splitext(fld_)
    return fld_


def expandpath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))