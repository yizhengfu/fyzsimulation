#!/bin/bash

# 提交任务到指定的CPU范围
sbatch -p sn \
    --ntasks=12 \
    --cpu-bind=v,map_cpu:0,1,2,3,4,5,6,7,8,9,10,11 \
    cp2k

sleep 2

sbatch -p sn \
    --ntasks=12 \
    --cpu-bind=v,map_cpu:12,13,14,15,16,17,18,19,20,21,22,23 \
    cp2k

# 如果需要第三个任务（使用24-35核）
# submit_job 24 12

# 如果需要第四个任务（使用36-47核）
# submit_job 36 12 