#!/bin/bash
sbatch -p sn --ntasks=24 --cpu-bind=socket_id:1 cp2k 1 