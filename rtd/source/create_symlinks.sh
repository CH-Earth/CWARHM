#!/bin/bash

for x in $(find . -type f -name '*.md' | sort); do name=`echo $x | tr -d \/ | sed "s/^.//g"`;ln -s `pwd`/$x rtd/source/$name;  done