#!/bin/bash
#Perform AIMD simulation at multiple temperatures
#Using all 28 cores for each temperature calculation sequentially
 
template_file=aimd_template.inp   #Template file for AIMD, temperature will be replaced
temp_list=temperatures.txt   #File containing temperature list (one temperature per line)
cp2k_bin=cp2k.popt   #CP2K command
nproc_to_use=28   #Total number of CPU cores to use for each calculation
recalc=1  #0: Keep old folder and files if exist  1: Always remove them and recalculate

input_file=aimd.inp
output_file=aimd.out
summary_file=AIMD_summary.txt

if [ $recalc -eq 1 ] ; then
    echo "Running: rm -r temp_*"
    rm -r temp_*
fi
nline=`wc -l $temp_list |cut -d ' ' -f 1`
echo "Number of AIMD simulations at different temperatures: $nline"

#Prepare input files
for ((i = 1; i <= $nline; i++)) ; do
    temp_this=$(awk -v iline=$i 'NR==iline' $temp_list)
    work_dir=temp_${temp_this}K
    if [ ! -d $work_dir ] ; then
        mkdir $work_dir
    fi
    # Replace TEMPERATURE placeholder with actual temperature value
    sed -e "s/TEMPERATURE PLACEHOLDER/TEMPERATURE ${temp_this}/g" $template_file > $work_dir/$input_file
done

#Run input files sequentially, using all 28 cores for each calculation
for ((i = 1; i <= $nline; i++)) ; do
    temp_this=$(awk -v iline=$i 'NR==iline' $temp_list)
    work_dir=temp_${temp_this}K
    cd $work_dir
    if [ ! -e $output_file ] ; then
        echo "Running AIMD at ${temp_this}K in $work_dir using $nproc_to_use cores"
        echo "Start time: $(date)"
        time mpirun -np $nproc_to_use $cp2k_bin -o $output_file $input_file
        echo "End time: $(date)"
    else
        echo "$work_dir/$output_file has existed, skip calculation"
    fi
    cd ..
done

#Analysis - Create a summary of the AIMD runs
echo "# AIMD simulations at different temperatures" > $summary_file
echo "# Date: $(date)" >> $summary_file
echo "# PWD: $PWD" >> $summary_file
echo -e "# Temperature (K) | Average Energy (Hartree) | Avg. Temperature (K) | Runtime (s)" >> $summary_file

for ((i = 1; i <= $nline; i++)) ; do
    temp_this=$(awk -v iline=$i 'NR==iline' $temp_list)
    work_dir=temp_${temp_this}K

    # Extract average energy from the last 1000 steps (adjust as needed)
    if [ -e "$work_dir/$output_file" ]; then
        avg_energy=$(grep "ENERGY| Total FORCE_EVAL" $work_dir/$output_file | tail -1000 | awk '{sum+=$9} END {print sum/NR}')
        avg_temp=$(grep "TEMPERATURE " $work_dir/$output_file | tail -1000 | awk '{sum+=$9} END {print sum/NR}')
        runtime=$(grep "CP2K   " $work_dir/$output_file | grep "seconds" | awk '{print $6}')

        # If values were found, add them to the summary
        if [ ! -z "$avg_energy" ] && [ ! -z "$avg_temp" ] && [ ! -z "$runtime" ]; then
            printf "    %4d K       %18.10f    %8.2f K       %8.1f s\n" $temp_this $avg_energy $avg_temp $runtime >> $summary_file
        else
            echo "    $temp_this K       Calculation incomplete or error" >> $summary_file
        fi
    else
        echo "    $temp_this K       Output file not found" >> $summary_file
    fi
done

echo "If finished normally, now check $summary_file"