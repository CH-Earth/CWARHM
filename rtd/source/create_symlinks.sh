#!/bin/bash

for x in $(find ../.. -type f -name '*.md' | sort); 
do 
    name=$(echo $x | tr -d \/ | sed "s/^.//g" | sed "s/\.\.\.//g")

    printf ".. include:: $x\n\t:parser: myst_parser.sphinx_" > "$name.rst"


    # ln -s -f $x $name;  

done
