#!/bin/bash

script_dir=$(dirname $0)/../
abspath=$(readlink -e $script_dir)
#echo $abspath
uweb add uwebmanager uwebmanager.router.uwebmanager --directory="${abspath}"
uweb list
