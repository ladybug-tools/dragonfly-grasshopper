# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
This component downloads dragonfly, honeybee, and ladybug libraries.
_
It also installs all of the grasshopper components to:
C:\Users\%USERNAME%\AppData\Roaming\Grasshopper\UserObjects
_
It also installs the honeybee_openstudio_gem to:
ladybug_tools\openstudio\honeybee_openstudio_gem
_
If stadnards are not found on this machine, it also installs standards to:
ladybug_tools\resources\standards
-

    Args:
        _update: Set to True to install dragonfly, honeybee and ladybug to your
            machine from the Ladybug Tools github.
        clean_standards_: Set to True to have any user libraries of standards
            overwritten with the latest version from Ladybug Tools. If False
            or None, any existing standards will be left alone and new
            standards will only be downloaded if there aren't any found on
            this machine.
    
    Returns:
        Vviiiiiz!: !!!
"""

ghenv.Component.Name = "DF Installer"
ghenv.Component.NickName = "DFInstaller"
ghenv.Component.Message = '0.10.2'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "5 :: Developers"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import io
import xml.etree.ElementTree
import subprocess
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

    This function has been copied from ladybug_rhino.download.

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


def get_python_exe():
    """Get the path to the Python installed in the ladybug_tools folder.

    Will be None if Python is not installed.
    """
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    py_install = os.path.join(home_folder, 'ladybug_tools', 'python')
    py_exe_file = os.path.join(py_install, 'python.exe') if os.name == 'nt' else \
        os.path.join(py_install, 'bin', 'python3')
    if os.path.isfile(py_exe_file):
        return py_exe_file
    return None


def get_python_package_dir():
    """Get the path to where Python packages are installed in the ladybug_tools folder.

    If the folder is not found, this method will create the folder.
    """
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    py_install = os.path.join(home_folder, 'ladybug_tools', 'python')
    py_path = os.path.join(py_install, 'Lib', 'site-packages') if os.name == 'nt' \
        else os.path.join(py_install, 'lib', 'python3.8', 'site-packages')
    if not os.path.isdir(py_path):
        return os.makedirs(py_path)
    return py_path


def get_measure_directory():
    """Get the directory where OpenStudio BCL measures are installed."""
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    measure_folder = os.path.join(home_folder, 'ladybug_tools', 'openstudio')
    if not os.path.isdir(measure_folder):
        os.makedirs(measure_folder)
    return measure_folder


def get_standards_directory():
    """Get the directory where Honeybee standards are installed."""
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    hb_folder = os.path.join(home_folder, 'ladybug_tools', 'resources', 'standards')
    if not os.path.isdir(hb_folder):
        os.makedirs(hb_folder)
    return hb_folder


def get_old_library_directory():
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


def clean_old_library_directory(repos, target_directory):
    """Remove installed packages from the old library directory.

    This will avoid namespace conflicts.

    Args:
        repos: An array of all repo names to be cleaned.
            (eg. ['honeybee-energy', 'ladybug-geometry']).
        target_directory: The directory to be cleaned.
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


def iron_python_search_path_windows(python_package_dir, iron_python_path=None):
    """Set Rhino to search for libraries in a given directory.

    This is used as part of the installation process to ensure that Grasshopper
    looks for the core Python libraries in

    Args:
        python_package_dir: The path to a directory that contains the Ladybug
            Tools core libraries.
    """
    # find the path to the IronPython plugin
    if iron_python_path is None:
        home_folder = os.getenv('HOME') or os.path.expanduser('~')
        plugin_folder = os.path.join(home_folder, 'AppData', 'Roaming', 'McNeel',
                                     'Rhinoceros', '6.0', 'Plug-ins')
        for plugin in os.listdir(plugin_folder):
            if plugin.startswith('IronPython'):
                iron_python_path = os.path.join(plugin_folder, plugin)
                break

    # open the settings file and find the search paths
    set_file = os.path.join(iron_python_path, 'settings', 'settings-Scheme__Default.xml')
    with io.open(set_file, 'r', encoding='utf-8') as fp:
        set_data = fp.read()
    element = xml.etree.ElementTree.fromstring(set_data)
    settings = element.find('settings')
    search_path_needed = True
    for entry in settings.iter('entry'):
        if 'SearchPaths' in list(entry.attrib.values()):
            if entry.text == python_package_dir:
                search_path_needed = False

    # add the search paths if it was not found
    if search_path_needed:
        line_to_add = '    <entry key="SearchPaths">{}</entry>\n'.format(python_package_dir)
        with open(set_file, 'r') as fp:
            contents = fp.readlines()
        for i, line in enumerate(contents):
            if 'ScriptForm_Location' in line:
                break
        contents.insert(i + 1, line_to_add)
        with open(set_file, 'w') as fp:
            fp.write(''.join(contents))
        sys.path.append(python_package_dir)


def update_libraries_pip(python_exe):
    """Update the core libraries using pip, which installs Ladybug Tools CLI.

    Args:
        python_exe: The path to the Python executable to be used for installation.
        """
    print('Installing Ladybug Tools core Python libraries via pip '
          'using\n{}'.format(python_exe))
    cmds = [python_exe, '-m', 'pip', 'install', 'lbt-dragonfly[cli]', '-U']
    cmd = ' '.join(cmds)
    process = subprocess.Popen(cmds, shell=True, stderr=subprocess.PIPE)
    output = process.communicate()
    stderr = output[-1]
    print(stderr)  # print any errors if they occurred


def update_libraries_github(repos, target_directory):
    """Download Ladybug Tools libraries from github.
    
    Args:
        repos: An array of all repo names to be installed.
            (eg. ['honeybee-energy', 'ladybug-geometry']).
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
            (eg. ['honeybee-openstudio-gem']).
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

# core libraries to be updated
libraries = \
    ('ladybug-rhino', 'ladybug-geometry', 'ladybug-geometry-polyskel',
     'ladybug', 'ladybug-comfort', 'honeybee-core', 'honeybee-energy',
     'honeybee-radiance', 'honeybee-radiance-folder', 'honeybee-radiance-command',
     'dragonfly-core', 'dragonfly-energy')


if _update:
    # update the core libraries
    update_libraries_github(libraries, get_old_library_directory())
    py_exe = get_python_exe()
    if py_exe is not None:  # python is installed correctly; use pip
        update_libraries_pip(py_exe)

    # update the standards files
    standards = ['honeybee-standards', 'honeybee-energy-standards']
    stand_dir = get_standards_directory()
    if not clean_standards_:
        packages = [os.path.join(stand_dir, pkg_name.replace('-', '_'))
                    for pkg_name in standards]
        standards = [standards[i] for i, lib_folder in enumerate(packages)
                     if not os.path.isdir(lib_folder)]
    if len(standards) != 0:
        update_libraries_github(standards, get_standards_directory())

    # update the grasshopper components
    components = \
        ('ladybug-grasshopper', 'honeybee-grasshopper-core',
         'honeybee-grasshopper-radiance', 'honeybee-grasshopper-energy',
         'dragonfly-grasshopper')
    update_components(components)

    # update the ruby gem
    gems = ('honeybee-openstudio-gem',)
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