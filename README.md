# LinuxModManager

**What is a mod manager?**
It's a tool that merges folders with an overwrite policy. That's it!

Linux has symlinks, so 90% of the work is done, i just need a script.

I wrote it in python over an evening so i could play StardewValley. I'll expand it and port it to rust or somehting when i feel like it.

# Docs

## Usage
### module
A module is a folder structure that will be merged into the target during the build-stage. Either a single mod, or a group of mods added together.

```
python3 clmod.py module list
```
Lists all modules.

```
python3 clmod.py module add
```
Adds a module. Will ask if it should clone the folder-structure of the target or not during creation.

```
python3 clmod.py module remove
```
Removes a module from the module list.

```
python3 clmod.py module prune
```
Prunes empty directories from all modules. Useful to clear out the extra folders after using ``module add``.


```
python3 clmod.py module add-from-diff
```
Clears away all symlinks from target, and turns what is remaining into a module. Can be used to tuwn all modified files from a installer into a module to keep the base-game clean. **Note: only works if config is set to symlink mode**

### target
The targer is the main game folder in which all sources will be merged to. 

```
python3 clmod.py target setup
```
Move the target folder content to the *_core* folder to protect it from modifications. 

```
python3 clmod.py target restore
```
Clear our the target folder and restore it with the content from the *_core*, to restore the game folder back to the initial stage. Helpful for game updates or file-integrity checks.

```
python3 clmod.py target init
```
Creates and fills out a config file, and calls *setup*.

```
python3 clmod.py target build
```
Merges all sources into the target folder. Assumes a empty target folder.


```
python3 clmod.py target rebuild
```
Merges all sources into the target folder. Resets the target before operation. Only files specified in the *exceptions list* will be excempted from being overwritten.


### config
Config settings
```
python3 clmod.py config list
```
Lists the current config settings

### exceptions
Use regx rules to protect files in the *target* from being overwritten during the build stage. This is particularly useful for config files.

```
python3 clmod.py exceptions add
```
Adds a new exception to the exc exception list

```
python3 clmod.py exceptions remove
```
Removes an exception from the exception list

```
python3 clmod.py exceptions list
```
List all current excetion rules in the config

```
python3 clmod.py exceptions check
```
Runs every rule and lists all files in the *target* that it catches


## config options
```
{"overwrite": <True | False>}
```
This option decides if each module in the folder should overwrite the last, or skip files that already exists. The default behaviour of other mod-loaders are TRUE, so leave it at that as a default.

```
{
    "copy_core": <True | False>
    "copy_modules": <True | False>
}
```
Symlinks (softlinks) aren't perfect equivalent to copying files. In particular, symlinking executables causes some issues. This option was added to always copy and overwrite files instead of linking them until i figure out a nice way to selectivly copy the important files and linking the rest.

Mods are less linkley to encoutner this problem, so core and modules are seperated into different settings.

## Terminology
**build** - the merging of modules into the targer directory

**target** - the base game folder where the files will be merged

**module** - A folder that will be merged with the others during build

**symlink** - A linux shortcut that behaves almost* equivalent to the real file.

**config.json** the configuration that describes target, sources, and some settigs.

# Future plans
1. **Mod profiles**:
I wanna split the config into a general config and a profile config, so i can jump between modding profiles by just using a different modules list.
2. **Hardlink mode**: Hardlinks have some higher restrictions, but could solve my bugs with linking executables.
3. **Better help**: the help command isn't quite as fleshed out as it should be. 
4. **Better test enviroment**: I've written this script while using it for games. But some unit tests are needed now that i have a decent design i'm happy with.