# read through every file in target and print its content

#!/bin/bash

# specify the path
path_to_directory="./target"
# use find command to find all files and directories recursively
find -L "$path_to_directory" -type f -exec sh -c '
  for file do
    echo "\t$file"
    head -n 1 "$file"
  done
' sh {} +