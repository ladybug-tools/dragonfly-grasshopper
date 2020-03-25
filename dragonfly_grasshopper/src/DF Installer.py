# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
This component downloads dragonfly, honeybee, and ladybug libraries from github to:
C:\Users\%USERNAME%\AppData\Roaming\McNeel\Rhinoceros\6.0\scripts
_
It also installs all of the grasshopper components from github to:
C:\Users\%USERNAME%\AppData\Roaming\Grasshopper\UserObjects
_
It also installs the energy_model_measure from github to:
ladybug_tools\energy_model_measure
_
If keep_standards is not True, it also installs standards from github to:
ladybug_tools\resources\standards
-

    Args:
        _update: Set to True to install dragonfly, honeybee and ladybug to your
            machine from the Ladybug Tools github.
        keep_standards_: Set to False to ensure that user libraries of standards
            are not overwritten by this component. If True or None, the libraries
            will be overwritten.
    
    Returns:
        Vviiiiiz!: !!!
"""

ghenv.Component.Name = "DF Installer"
ghenv.Component.NickName = "DFInstaller"
ghenv.Component.Message = '0.7.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "5 :: Developers"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import System.Net
import sys
import zipfile
import shutil
from distutils import dir_util
from Grasshopper.Folders import UserObjectFolders


def preparedir(target_dir, remove_content=True):
    """Prepare a folder for files to be written into it.

    This function creates the folder if it does not exist and removes the files in
    the folder if the folder already exists.

    This function has been copied from ladybug.futil.
    """
    if os.path.isdir(target_dir):
        if remove_content:
            nukedir(target_dir, False)
        return True
    else:
        try:
            os.makedirs(target_dir)
            return True
        except Exception as e:
            print("Failed to create folder: %s\n%s" % (target_dir, e))
            return False


def nukedir(target_dir, rmdir=False):
    """Delete all the files inside target_dir.

    This function has been copied from ladybug.futil.
    """
    d = os.path.normpath(target_dir)
    if not os.path.isdir(d):
        return

    files = os.listdir(d)
    for f in files:
        if f == '.' or f == '..':
            continue
        path = os.path.join(d, f)
        if os.path.isdir(path):
            nukedir(path)
        else:
            try:
                os.remove(path)
            except Exception:
                print("Failed to remove %s" % path)

    if rmdir:
        try:
            os.rmdir(d)
        except Exception:
            try:
                dir_util.remove_tree(d)
            except Exception:
                print("Failed to remove %s" % d)


def copy_file_tree(source_folder, dest_folder, overwrite=True):
    """Copy an entire file tree from a source_folder to a dest_folder.

    Args:
        source_folder: The source folder containing the files and folders to
            be copied.
        dest_folder: The destination folder into which all the files and folders
            of the source_folder will be copied.
        overwrite: Boolean to note whether an existing folder with the same
            name as the source_folder in the dest_folder directory should be
            overwritten. Default: True.
    """
    # make the dest_folder if it does not exist
    if not os.path.isdir(dest_folder):
        os.mkdir(dest_folder)

    # recursively copy each sub-folder and file
    for f in os.listdir(source_folder):
        # get the source and destination file paths
        src_file_path = os.path.join(source_folder, f)
        dst_file_path = os.path.join(dest_folder, f)

        # if overwrite is True, delete any existing files
        if overwrite:
            if os.path.isfile(dst_file_path):
                try:
                    os.remove(dst_file_path)
                except Exception:
                    raise IOError("Failed to remove %s" % f)
            elif os.path.isdir(dst_file_path):
                nukedir(dst_file_path, True)

        # copy the files and folders to their correct location
        if os.path.isfile(src_file_path):
            shutil.copyfile(src_file_path, dst_file_path)
        elif os.path.isdir(src_file_path):
            if not os.path.isdir(dst_file_path):
                os.mkdir(dst_file_path)
            copy_file_tree(src_file_path, dst_file_path, overwrite)


def download_file_by_name(url, target_folder, file_name, mkdir=False):
    """Download a file to a directory.

    This function has been copied from ladybug_dotnet.download.

    Args:
        url: A string to a valid URL.
        target_folder: Target folder for download (e.g. c:/ladybug)
        file_name: File name (e.g. testPts.zip).
        mkdir: Set to True to create the directory if doesn't exist (Default: False)
    """
    # create the target directory.
    if not os.path.isdir(target_folder):
        if mkdir:
            preparedir(target_folder)
        else:
            created = preparedir(target_folder, False)
            if not created:
                raise ValueError("Failed to find %s." % target_folder)
    file_path = os.path.join(target_folder, file_name)

    # set the security protocol to the most recent version
    try:
        # TLS 1.2 is needed to download over https
        System.Net.ServicePointManager.SecurityProtocol = \
            System.Net.SecurityProtocolType.Tls12
    except AttributeError:
        # TLS 1.2 is not provided by MacOS .NET
        if url.lower().startswith('https'):
            print ('This system lacks the necessary security'
                   ' libraries to download over https.')

    # attempt to download the file
    client = System.Net.WebClient()
    try:
        client.DownloadFile(url, file_path)
    except Exception as e:
        raise Exception(' Download failed with the error:\n{}'.format(e))


def unzip_file(source_file, dest_dir=None, mkdir=False):
    """Unzip a compressed file.

    This function has been copied from ladybug.futil.

    Args:
        source_file: Full path to a valid compressed file (e.g. c:/ladybug/testPts.zip)
        dest_dir: Target folder to extract to (e.g. c:/ladybug).
            Default is set to the same directory as the source file.
        mkdir: Set to True to create the directory if doesn't exist (Default: False)
    """
    # set default dest_dir and create it if need be.
    if dest_dir is None:
        dest_dir, fname = os.path.split(source_file)
    elif not os.path.isdir(dest_dir):
        if mkdir:
            preparedir(dest_dir)
        else:
            created = preparedir(dest_dir, False)
            if not created:
                raise ValueError("Failed to find %s." % dest_dir)

    # extract files to destination
    with zipfile.ZipFile(source_file) as zf:
        for member in zf.infolist():
            words = member.filename.split('\\')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                dest_dir = os.path.join(dest_dir, word)
            zf.extract(member, dest_dir)


def get_library_directory():
    """Get the Rhino directory into which the Python libraries will be installed."""
    try:
        target_directory = [p for p in sys.path if p.find('scripts')!= -1][0]
    except IndexError:  # there is no scripts in path; try to find plugins folder
        try:
            target_directory = [p for p in sys.path if p.find(r'settings\lib')!= -1][0]
        except IndexError:  # there's no plugins folder; we might be on a Mac
            try:
                target_directory = [p for p in sys.path if p.find(r'Lib')!= -1][0]
            except IndexError:  # I don't know where we are at this point
                raise IOError(
                    'Failed to find a shared path in sys.path to install the libraries.\n' \
                     'Make sure Grasshopper is installed correctly!')
    return target_directory


def get_measure_directory():
    """Get the directory where OpenStudio BCL measures are installed."""
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    meas_folder = os.path.join(home_folder, 'ladybug_tools')
    if not os.path.isdir(meas_folder):
        os.makedirs(meas_folder)
    return meas_folder


def get_standards_directory():
    """Get the directory where Honeybee standards are installed."""
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    hb_folder = os.path.join(home_folder, 'ladybug_tools', 'resources', 'standards')
    if not os.path.isdir(hb_folder):
        os.makedirs(hb_folder)
    return hb_folder


def update_libraries(repos, target_directory):
    """Download Ladybug Tools libraries from github.
    
    Args:
        repos: An array of all repo names to be installed.
            (eg. ['ladybug', 'ladybug-geometry']).
        target_directory: the directory where the Python libraries should
            be copied.
        """

    # derive the distribution package name from the repo name
    packages = []
    for f in repos:
        pkg_name = f.replace('-core', '') if f.endswith('-core') else f
        packages.append(pkg_name.replace('-', '_'))

    # delete currently-installed packages if they exist 
    for pkg in packages:
        lib_folder = os.path.join(target_directory, pkg)
        if os.path.isdir(lib_folder):
            print 'Removing {}'.format(lib_folder)
            nukedir(lib_folder)

    # download and unzip files
    for repo in repos:
        # download files
        url = "https://github.com/ladybug-tools/%s/archive/master.zip" % repo
        zip_file = os.path.join(target_directory, '%s.zip' % repo)
        print "Downloading {} the github repository to {}".format(repo, target_directory)
        download_file_by_name(url, target_directory, zip_file)

        #unzip the file
        unzip_file(zip_file, target_directory)

        # try to clean up the downloaded zip file
        try:
            os.remove(zip_file)
        except:
            print 'Failed to remove downloaded zip file: {}.'.format(zip_file)

    # copy files to folder
    for f, p in zip(repos, packages):
        source_folder = os.path.join(target_directory, r"{}-master".format(f), p) if 'standards' \
            not in f else os.path.join(target_directory, r"{}-master".format(f), p, 'data')
        lib_folder = os.path.join(target_directory, p)
        if 'standards' in f:
            for sub_dir in os.listdir(source_folder):
                if os.path.isdir(os.path.join(source_folder, sub_dir)) and not \
                        os.path.isdir(os.path.join(lib_folder, sub_dir)):
                    os.makedirs(os.path.join(lib_folder, sub_dir))
        print 'Copying {} library source code to {}'.format(f, lib_folder)
        dir_util.copy_tree(source_folder, lib_folder)

    # try to clean up
    for r in repos:
        try:
            nukedir(os.path.join(target_directory, '{}-master'.format(r)), True)
        except:
            print 'Failed to clean up downloaded library: {}'.format(r)


def update_components(repos):
    """Download Ladybug Tools Grasshopper components from github.
    
    Args:
        repos: An array of all repo names to be installed.
            (eg. ['ladybug=grasshopper', 'honeybee-grasshopper-core']).
    """

    # derive the distribution package name from the repo name
    packages = [f.replace('-', '_') for f in repos]

    # get the directory where the user objects should be copied
    target_directory = UserObjectFolders[0]
    
    # delete currently-installed packages of components if they exist 
    for pkg in packages:
        lib_folder = os.path.join(target_directory, pkg)
        if os.path.isdir(lib_folder):
            print 'Removing {}'.format(lib_folder)
            nukedir(lib_folder)

    # download and unzip files
    for repo in repos:
        # download files
        url = "https://github.com/ladybug-tools/%s/archive/master.zip" % repo
        zip_file = os.path.join(target_directory, '%s.zip' % repo)
        print "Downloading {} the github repository to {}".format(repo, target_directory)
        download_file_by_name(url, target_directory, zip_file)

        #unzip the file
        unzip_file(zip_file, target_directory)

        # try to clean up the downloaded zip file
        try:
            os.remove(zip_file)
        except:
            print 'Failed to remove downloaded zip file: {}.'.format(zip_file)

    # copy the user object package to the folder
    for f, p in zip(repos, packages):
        source_folder = os.path.join(target_directory, r"{}-master".format(f), p)
        lib_folder = os.path.join(target_directory, p)
        print 'Copying {} user objects to {}'.format(f, lib_folder)
        dir_util.copy_tree(source_folder, lib_folder)

    # try to clean up
    for r in repos:
        try:
            nukedir(os.path.join(target_directory, '{}-master'.format(r)), True)
        except:
            print 'Failed to clean up downloaded components: {}'.format(r)


def update_gems(repos):
    """Download Ladybug Tools Ruby gems from github.
    
    Args:
        repos: An array of all repo names to be installed.
            (eg. ['energy-model-measure']).
        """

    # derive the gem name from the repo name
    packages = []
    for f in repos:
        packages.append(f.replace('-', '_'))

    # get the directory where the measure should be copied
    target_directory = get_measure_directory()

    # delete currently-installed packages if they exist 
    for pkg in packages:
        lib_folder = os.path.join(target_directory, pkg)
        if os.path.isdir(lib_folder):
            print 'Removing {}'.format(lib_folder)
            nukedir(lib_folder)

    # download and unzip files
    for repo in repos:
        # download files
        url = "https://github.com/ladybug-tools-in2/%s/archive/master.zip" % repo
        zip_file = os.path.join(target_directory, '%s.zip' % repo)
        print "Downloading {} the github repository to {}".format(repo, target_directory)
        download_file_by_name(url, target_directory, zip_file)

        #unzip the file
        unzip_file(zip_file, target_directory)

        # try to clean up the downloaded zip file
        try:
            os.remove(zip_file)
        except:
            print 'Failed to remove downloaded zip file: {}.'.format(zip_file)

    # rename the folder
    for f, p in zip(repos, packages):
        source_folder = os.path.join(target_directory, r"{}-master".format(f), 'lib')
        lib_folder = os.path.join(target_directory, p, 'lib')
        print 'Copying {} library source code to {}'.format(f, lib_folder)
        copy_file_tree(source_folder, lib_folder)

    # try to clean up
    for r in repos:
        try:
            nukedir(os.path.join(target_directory, '{}-master'.format(r)), True)
        except:
            print 'Failed to clean up downloaded library: {}'.format(r)


if _update:
    # update the core libraries
    libraries = \
        ('ladybug', 'ladybug-geometry', 'ladybug-rhino', 'ladybug-dotnet', 'ladybug-comfort',
         'honeybee-core', 'honeybee-energy', 'dragonfly-core', 'dragonfly-energy')
    update_libraries(libraries, get_library_directory())
    
    # update the standards files
    if not keep_standards_:
        standards = ('honeybee-standards', 'honeybee-energy-standards')
        update_libraries(standards, get_standards_directory())
    
    # update the grasshopper components
    components = \
        ('ladybug-grasshopper', 'honeybee-grasshopper-core',
         'honeybee-grasshopper-energy', 'dragonfly-grasshopper')
    update_components(components)
    
    # update the ruby gems
    gems = ('energy-model-measure',)
    update_gems(gems)
    
    # check to be sure that the new libraries can be imported
    try:
        import ladybug
        import honeybee
        import dragonfly
    except ImportError as e:
        raise ImportError('Failed to import libraries:\n{}'.format(e))
    else:
        print "\n\nImported libraries from {}\nVviiiizzzz...".format(ladybug.__file__)
        print "\n\nImported libraries from {}\nVviiiizzzz...".format(honeybee.__file__)
        print "\n\nImported libraries from {}\nVviiiizzzz...".format(dragonfly.__file__)
        print "Restart Grasshopper and Rhino to load the new library."
else:  # give a message to the user about what to do
    print 'Make sure you are connected to the internet and set _update to True!'