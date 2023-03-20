#!/bin/bash

cd /home/dionnys/AguilappsBots/

# Activar el entorno virtual de Python
. env/bin/activate

# Ejecutar el archivo Python con los parámetros
python aguilapps.py -q $1

deactivate