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
   
    action = "added"
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
                action = "overwrote"
            else:
                # skip the file
                print(f"  Skipped {f.path}")
                continue

        # symlink the file
        
        if copy:
            action = "copied"
            shtil.copy(absolute_path(f.path), absolute_path(target_file))
            
        else:
            action = "softlinked"
            os.symlink(absolute_path(f.path), absolute_path(target_file))
            
        if verbose:
            print(f"  {action} {target_file}")

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

        merge(f.path, target_file, depth + 1, overwrite=overwrite, verbose=verbose, copy=copy)

def merge_structure(source_path, target_path, depth=0, verbose=False):
    # for all directories, recursively call the merge function
    for f in os.scandir(source_path):
        # if the file is a directory
        if not f.is_dir():
            continue

        target_file = os.path.join(target_path, f.name)
        exist = os.path.exists(target_file)

        if not exist:
            os.mkdir(absolute_path(target_file))
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
        try:
            config['target_path'] = conf['target']
            config['source_root'] = conf['source_root']
            config['overwrite'] = conf['overwrite']
            config['copy_core'] = conf['copy_core']
            config['copy_modules'] = conf['copy_modules']
            config['exceptions'] = conf['exceptions']

            config['source_paths'] = [os.path.join(conf['source_root'], s) for s in conf['sources']]
            config['core_path'] = os.path.join(conf['source_root'], "_core")
        except KeyError:
            assert False, "Config file is not valid"
        
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
        if verbose:
            print("Merging core")
        merge(config["core_path"], config['target_path'], verbose=False, overwrite=True, copy=copy_core)
    
    for source in config["source_paths"]:
        if verbose:
            print(f"Merging source {source}")
        merge(source, config['target_path'], overwrite=overwrite, verbose=False, copy=copy_modules)
    
    return

# main runner

def prune(path , verbose=False):
    # for each module in the source paths
    # check if the path exists
    if not os.path.exists(path):
        return

    clear_symlinks(path, verbose=verbose)

def prune_multiple(paths: list, verbose=False):
    for path in paths:
        prune(path, verbose=verbose)

def eval_exceptions(config, rule):
   
    # for all files in exception, move from target to source
    
    import glob

    files = glob.glob(rule, root_dir=config["target_path"], recursive=True)
    files = [f for f in files if not os.path.islink(os.path.join(config["target_path"], f))]
    
    return files

def list_affected_exceptions(config):
    exceptions = []
    for rule in config['exceptions']:
        excepts = eval_exceptions(config, rule)
        print(f"evaluating rule {rule}")
        [print(f"  found {f}") for f in excepts]
    
    return exceptions

def save_exceptions(config, verbose=False):
    exceptions_path = os.path.join(config["source_root"], "_exceptions")
    
    if not os.path.exists(exceptions_path):
        os.mkdir(exceptions_path)
    
    clear_path(exceptions_path)
    merge_structure(config['target_path'], exceptions_path, verbose=False)
    
    for rule in config['exceptions']:
        if verbose:
            print(f"evaluating rule {rule}")
        
        excepts = eval_exceptions(config, rule)
        
        for f in excepts:
            target_file = os.path.join(config['target_path'], f)
            source_file = os.path.join(exceptions_path, f)
            
            action = "saved"
            
            # move the file
            try:
                shtil.copy(absolute_path(target_file), absolute_path(source_file))
                # wait for the file to be copied
            except:
                action = "failed"
            
            if verbose:
                print(f"  {action} {absolute_path(source_file)}")
    
    prune(exceptions_path, verbose=verbose)
        
def load_exceptions(config, verbose=False):
    exceptions_path = os.path.join(config["source_root"], "_exceptions")
    
    if not os.path.exists(exceptions_path):
        print("no eceptions found in exceptions folder")
        return
    
    merge(exceptions_path, config['target_path'], copy=True, verbose=verbose, overwrite=True)


def config_runner(command,config, verbose=False):
    if command == "list":
        print(f"Target: {config['target_path']}")
        print(f"Source root: {config['source_root']}")
        print(f"Overwrite: {config['overwrite']}")
        print(f"Copy core: {config['copy_core']}")
        print(f"Copy modules: {config['copy_modules']}")
        print(f"Exceptions: {config['exceptions']}")

def exceptions_runner(command,config,verbose=False):
    
    if command == "save":
        save_exceptions(config, verbose=verbose)
    
    elif command == "check":
        list_affected_exceptions(config)
    
    elif command == "load":
        load_exceptions(config, verbose=verbose)
    
    elif command == "list":
        print("Exceptions: []")
        for rule in config['exceptions']:
            print(f"  {rule}")

    elif command == "add":
        rule = input("Rule: ")
        config['exceptions'].append(rule)
        save_config(config, config['source_root'], "config.json")

    elif command == "remove":
        for rule in config['exceptions']:
            print(f"  {rule}")
        ruleid = input("Rule_id: ")
        config['exceptions'].pop(ruleid)

def module_runner(command,config, verbose=False, name=None):
    if command == "list":
        print("Sources: []")
        for path in config["source_paths"]:
            print(f"  {path}")
        
        print("")
        print(f"Target: {config['target_path']}")
    
    elif command == "add":
        if name is None:
            name = input("Name of the module: ")
        name = input("Name of the module: ")
        copy = input("Copy folder structure from target? (y/n): ")
        copy = copy.lower() == "y"
        create_module(config, name, copy, verbose)
        
        # save to config
        config['source_paths'].append(os.path.join(config['source_root'], name))
        save_config(config, config['source_root'], "config.json")
        return

    elif command == "remove":
        if name is None:
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
        
    elif command == "add-from-diff":
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
        
    if command == "prune":
        prune(config, verbose=verbose)
         
def target_runner(command,config,verbose=False):
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
    
    if command == "setup":
        setup(config)
        return

    if command == "restore":
        save_exceptions(config, verbose=verbose)
        restore(config)
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
    
def runner(catagory, command, flags):
    config = load_config(".")

    verbose = flags.verbose

    if catagory == "config":
        config_runner(command,config, verbose=verbose)
    elif catagory == "exceptions":
        exceptions_runner(command,config, verbose=verbose)
    elif catagory == "module":
        name = flags.name
        if name == "":
            name = None
        
        module_runner(command,config, verbose=verbose, name=name)
    elif catagory == "target":
        target_runner(command,config, verbose=verbose)

if __name__ == "__main__":
        
    # get all flags from terminal
    args = os.sys.argv
    import argparse
    parser = argparse.ArgumentParser(description='CLMod')
    parsers = parser.add_subparsers(dest='catagory', help='subcommand to execute')

    config_parser = parsers.add_parser('config', help='Configure the profile json file')
    config_parser.add_argument('command', type=str, help='Config action', choices=['init', 'list'])
    config_parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

    exceptions_parser = parsers.add_parser('exceptions', help='Configure the exceptions that should be protected from deletion')
    exceptions_parser.add_argument('command', type=str, help='Exceptions action', choices=['save', 'load', 'list', 'add', 'remove', 'check'])
    exceptions_parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

    module_parser = parsers.add_parser('module', help='Add and remove modules from the load-order')
    module_parser.add_argument('command', type=str, help='Module action', choices=['add', 'remove', 'add-from-diff'])
    module_parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    module_parser.add_argument('-n', '--name', default="", type=str, help='name of the module')
    
    builder_parser = parsers.add_parser('target', help='Build the target directory from the config and sources')
    builder_parser.add_argument('command', type=str, help='Builder action', choices=['build', 'rebuild', 'setup', 'restore'])
    builder_parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

    # verbose flag 
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

    args = parser.parse_args()
    catagory = args.catagory
    command = args.command

    runner(catagory, command, args)

