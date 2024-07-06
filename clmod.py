import os

import shutil as shtil

import json

def path_is_empty(path):
    # check if the target path is empty
    return len(os.listdir(path)) == 0

def absolute_path(path):
    return os.path.abspath(path)

def clear_path(path):
    # delete folder and its content
    shtil.rmtree(path)

    # create the folder again
    os.mkdir(path)

def merge(source_path, target_path, depth=0, overwrite=False, verbose=False, copy=False):
    print(f"{'  ' * depth}Merging {source_path} to {target_path}")

    # symlink all files in the source directory to the target directory
    for f in os.scandir(source_path):
        if not f.is_file():
            continue
    
        target_file = os.path.join(target_path, f.name)
        exist = os.path.exists(target_file) or os.path.islink(target_file)

        # if the file already exists in the target directory
        if exist:
            if overwrite:
                # remove the symlink or file
                os.remove(target_file)
                if verbose:
                    print(f"{'  ' * depth} Removed {target_file}")
            else:
                # skip the file
                print(f"{'  ' * depth} Skipping {f.path}")
                continue

        # symlink the file
        
        if not copy:
            os.symlink(absolute_path(f.path), target_file)
        else:
            shtil.copy(absolute_path(f.path), absolute_path(target_file))
            
        if verbose:
            print(f"{'  ' * depth} Symlinked {f.path} to {target_path}")

    # for all directories, recursively call the merge function
    for f in os.scandir(source_path):
        # if the file is a directory
        if not f.is_dir():
            continue

        target_file = os.path.join(target_path, f.name)
        exist = os.path.exists(target_file) or os.path.islink(target_file)

        if not exist:
            os.mkdir(target_file)
            if verbose:
                print(f"{'  ' * depth} Created directory {target_file}")

        merge(f.path, target_file, depth + 1, overwrite, verbose)

def merge_structure(source_path, target_path, depth=0, verbose=False):
    # for all directories, recursively call the merge function
    for f in os.scandir(source_path):
        # if the file is a directory
        if not f.is_dir():
            continue

        target_file = os.path.join(target_path, f.name)
        exist = os.path.exists(target_file) or os.path.islink(target_file)

        if not exist:
            os.mkdir(target_file)
            if verbose:
                print(f"{'  ' * depth} Created directory {target_file}")

        merge_structure(f.path, target_file, depth + 1, verbose)

def move(source_path, target_path, verbose=False):
    # ensure souce path exists
    assert os.path.exists(source_path), f"Path ({source_path}) does not exist"

    # get folder in which target is located
    target_folder = os.path.dirname(target_path)

    # move the source folder to the target location
    # remove the target folder if it exists
    if os.path.exists(target_path):
        # if empty
        if path_is_empty(target_path):
            os.rmdir(target_path)
        else:
            assert False, "Target folder is not empty"

    shtil.move(source_path, target_folder)
    
    # rename it to the target name
    basename = os.path.basename(source_path)
    os.rename(os.path.join(target_folder, basename), target_path)

    # re-create an empty folder in the source root
    os.mkdir(source_path)

def clear_symlinks(path, depth=0, verbose=False):
    # symlink all files in the source directory to the target directory
    for f in os.scandir(path):
        if not f.is_file():
            continue
            
        # if symlink remove
        if os.path.islink(f.path):
            os.remove(f.path)
    
    # for all directories, recursively call the merge function
    for f in os.scandir(path):
        # if the file is a directory
        if not f.is_dir():
            continue

        clear_symlinks(f.path, depth + 1, verbose)
    
    # for all empty folders, remove them
    for f in os.scandir(path):
        if not f.is_dir():
            continue

        if path_is_empty(f.path):
            os.rmdir(f.path)   

# CLI tool function

def load_config(config_path, config_name="config.json", verbose=False):
    config = {}
    # read souces and target from config.yaml
    with open(os.path.join(config_path, config_name)) as f:
        conf = json.load(f)
        config['target_path'] = conf['target']
        config['source_root'] = conf['source_root']
        config['overwrite'] = conf['overwrite']
        config['copy_core'] = conf['copy_core']
        config['copy_modules'] = conf['copy_modules']
        config['exceptions'] = conf['exceptions']

        config['source_paths'] = [os.path.join(conf['source_root'], s) for s in conf['sources']]
        config['core_path'] = os.path.join(conf['source_root'], "_core")
        
    # check if the target path exists
    if not os.path.exists(config['target_path']):
        os.mkdir(config['target_path'])
        if verbose:
            print(f"Created target path ({config['target_path']})")

    # check if the source root exists
    if not os.path.exists(config['source_root']):
        os.mkdir(config['source_root'])
        if verbose:
            print(f"Created source root ({config['source_root']})")
    
    # check if the sources paths exists
    for path in config['source_paths']:
        if not os.path.exists(path):
            os.mkdir(path)
            if verbose:
                print(f"Created source path ({path})")
    
    # check if the core path exists
    if not os.path.exists(config['core_path']):
        os.mkdir(config['core_path'])

    return config

def save_config(config, config_path, config_name="config.json", verbose=False):
    conf = {}
    conf['target'] = config['target_path']
    conf['source_root'] = config['source_root']
    conf['overwrite'] = config['overwrite']
    conf['sources'] = [os.path.relpath(s, config['source_root']) for s in config['source_paths']]
    conf['copy_core'] = config['copy_core']
    conf['copy_modules'] = config['copy_modules']
    conf['exceptions'] = config['exceptions']
    
    with open(os.path.join(config_path, config_name), "w") as f:
        json.dump(conf, f)

def setup(config, verbose=False):
     # check if the target path exists
    assert os.path.exists(config['target_path']), f"Target path ({config['target_path']}) does not exist"
    assert not path_is_empty(config['target_path']), "Target path is empty"

    if not os.path.exists(config['source_root']):
        try:
            os.mkdir(config['source_root'])
        except FileExistsError:
            assert False, f"unable to create source root ({config['source_root']})"

    # create the core_path
    if not os.path.exists(config["core_path"]):
        os.mkdir(config["core_path"])
        
    move(config['target_path'], config['core_path'])

def restore(config, verbose=False):
    assert os.path.exists(config['core_path']), f"Target path ({config['target_path']}) does not exist"
    assert not path_is_empty(config['core_path']), "Core path is empty"

    clear_path(config['target_path'])
    move(config['core_path'], config['target_path'])

def create_module(config, name, copy, verbose=False):
    path = os.path.join(config["source_root"], name)

    if not os.path.exists(path):
        os.mkdir(path)
        
        if copy:
            merge_structure(config["target_path"], path)
        
        print("empty module created")
    else:
        print(f"Path found, added to config")

def build(config, verbose=False):
    overwrite = config['overwrite']
    assert path_is_empty(config['target_path']), "Target directory is not empty"
    
    copy_core = config['copy_core']
    copy_modules = config['copy_modules']
    
    if os.path.exists(config['core_path']):
        merge(config["core_path"], config['target_path'], verbose=verbose, overwrite=True, copy=copy_core)
    
    for source in config["source_paths"]:
        merge(source, config['target_path'], overwrite=overwrite, verbose=verbose, copy=copy_modules)
    
    return

# main runner

def prune(config, verbose=False):
    # for each module in the source paths
    for path in config["source_paths"]:
        # check if the path exists
        if not os.path.exists(path):
            continue
    
        clear_symlinks(path, verbose=verbose)

def save_exceptions(config, verbose=False):
    
    exceptions_path = os.path.join(config["source_root"], "_exceptions")
    if not os.path.exists(exceptions_path):
        os.mkdir(exceptions_path)
    
    clear_path(exceptions_path)
    merge_structure(config['target_path'], exceptions_path)
    
    # for all files in exception, move from target to source
    
    import glob
    exceptions = []
    for rule in config['exceptions']:
        files = glob.glob(rule, root_dir=config["target_path"], recursive=True)
        if verbose:
            print("rule", rule)
            print("found: ")
            [print(f) for f in files]
        
        exceptions.extend(files)
    
    for f in exceptions:
        target_file = os.path.join(config['target_path'], f)
        source_file = os.path.join(exceptions_path, f)
        
        # move the file
        try:
            shtil.copy(target_file, source_file, follow_symlinks=True)
        except FileNotFoundError:
            if verbose:
                print(f"File not found: {f}")
            continue
        
def load_exceptions(config, verbose=False):
    exceptions_path = os.path.join(config["source_root"], "_exceptions")
    
    if not os.path.exists(exceptions_path):
        print("no eceptions found in exceptions folder")
        return
    
    merge(exceptions_path, config['target_path'], copy=True, verbose=verbose, overwrite=True)

def runner(command, flags=[]):
    # print working directory
    print(f"Working directory: {os.getcwd()}")

    # flags
    verbose = False
    if sum([f in flags for f in ['-v", "--verbose']]):
        verbose = True
        print("Verbose mode on")

    if command == "init":
        # target path
        config = {}
        config['target_path'] = input("Target path: ")
        config['source_root'] = input("Source root: ")
        config['core_path'] = os.path.join(config['source_root'], "_core")
        config['source_paths'] = []
        config['overwrite'] = True

        setup(config)
        # create config file
        save_config(config, config['source_root'], "config.json")

    # read config file
    if verbose:
        print("loading config...")
    config = load_config(".")
    print("loaded config!")
    
    if command == "list":
        print("Sources: []")
        for path in config["source_paths"]:
            print(f"  {path}")
        
        print("")
        print(f"Target: {config['target_path']}")
        return
    
    if command == "build":
        build(config, verbose=verbose)
        load_exceptions(config, verbose=verbose)
        return
    
    if command == "rebuild":
        save_exceptions(config, verbose=verbose)
        clear_path(config['target_path'])
        build(config, verbose=verbose)
        load_exceptions(config, verbose=verbose)
        return
    
    if command == "setup":
        setup(config)
        return

    if command == "restore":
        save_exceptions(config, verbose=verbose)
        restore(config)
        return

    if command == "add":
        name = input("Name of the module: ")
        copy = input("Copy folder structure from target? (y/n): ")
        copy = copy.lower() == "y"
        create_module(config, name, copy, verbose)
        
        # save to config
        config['source_paths'].append(os.path.join(config['source_root'], name))
        save_config(config, config['source_root'], "config.json")
        return

    if command == "remove":
        name = input("Name of the module: ")
        path = os.path.join(config['source_root'], name)
        if path in config['source_paths']:
            config['source_paths'].remove(path)
            save_config(config, config['source_root'], "config.json")
        
        # clear the path
        clear = input("Clear the module folder? (y/n): ")
        clear = clear.lower() == "y"
        if clear:
            clear_path(path)
            os.rmdir(path)
        return
    
    if command == "add-from-diff":
        name = input("Name of the module: ")
        clear_symlinks(config['target_path'], verbose=verbose)
        
        module_path = os.path.join(config['source_root'], name)
        # move remaining content to the module folder
        move(config['target_path'], module_path)
        
        # add the new module to the config
        
        config['source_paths'].append(module_path)
        save_config(config, config['source_root'], "config.json")
        
        # rebuild the target
        build(config, verbose=verbose)
        return 
    
    if command == "prune":
        prune(config, verbose=verbose)
        return
    
    # unrecognized command
    print(f"Unrecognized command: {command}")


# get all flags from terminal
args = os.sys.argv

if len(args) < 2:
    print("No command provided")
    exit()

command = args[1]
flags = args[2:]
flags = [f for f in flags if f.startswith("-")]

runner(command, flags)
