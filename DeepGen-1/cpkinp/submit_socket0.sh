#!/bin/bash
sbatch -p sn --ntasks=24 --cpu-bind=socket_id:0 cp2k 0 