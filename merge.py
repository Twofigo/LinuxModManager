import os

import shutil as shtil

import json

sources_paths = []
target_path = ""

def load_config():
    global sources_paths, target_path
    # read souces and target from config.yaml
    with open("config.json") as f:
        config = json.load(f)
        root = config["root"]
        sources_paths = [os.path.join(root, s) for s in config["sources"]]
        target_path = os.path.join(root, config["target"])

def validate_config():
    # check if the target path exists
    assert os.path.exists(target_path), f"Target path ({target_path}) does not exist"

    # check if the sources paths exists
    for path in sources_paths:
        assert os.path.exists(path), f"Source path ({path}) does not exist"

def target_empty():
    # check if the target path is empty
    return len(os.listdir(target_path)) == 0

def clear_target():
    # delete folder and its content
    shtil.rmtree(target_path)

    # create the folder again
    os.mkdir(target_path)

def merge(source, target, depth=0, overwrite=False, verbose=False):
    print(f"{'  ' * depth}Merging {source} to {target}")

    # symlink all files in the source directory to the target directory
    for f in os.scandir(source):
        if not f.is_file():
            continue
    
        target_file = os.path.join(target, f.name)
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
        os.symlink(f.path, target_file)
        if verbose:
            print(f"{'  ' * depth} Symlinked {f.path} to {target}")

    # for all directories, recursively call the merge function
    for f in os.scandir(source):
        # if the file is a directory
        if not f.is_dir():
            continue

        target_file = os.path.join(target, f.name)
        exist = os.path.exists(target_file) or os.path.islink(target_file)

        if not exist:
            os.mkdir(target_file)
            if verbose:
                print(f"{'  ' * depth} Created directory {target_file}")

        merge(f.path, target_file, depth + 1, overwrite, verbose)
    
def build(verbose=False, overwrite=False):
    global sources_paths, target_path

    assert target_empty(), "Target directory is not empty"
    
    for source in sources_paths:
        merge(source, target_path, overwrite=overwrite, verbose=verbose)

def runner(command, flags=[]):
    global sources_paths, target_path

    # switch case for the command
    print("loading config...")
    load_config()
    validate_config()
    print("loading successful!")
    
    # flags
    verbose = False
    if sum([f in flags for f in ["-v", "--verbose"]]):
        verbose = True
        print("Verbose mode on")

    overwrite = False
    if sum([f in flags for f in ["-o", "--overwrite"]]):
        overwrite = True

    if command == "list":
        print("Sources: []")
        for path in sources_paths:
            print(f"  {path}")
        
        print("")
        print(f"Target: {target_path}")
        return
    
    if command == "build":
        build(verbose)
        return
    
    if command == "clear":
        clear_target()
        return
    
    if command == "rebuild":
        clear_target()
        build(verbose)
        return

# get all flags from terminal
args = os.sys.argv

if len(args) < 2:
    print("No command provided")
    exit()

command = args[1]
flags = args[2:]
flags = [f for f in flags if f.startswith("-")]

runner(command, flags)
