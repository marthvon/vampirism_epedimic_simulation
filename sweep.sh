#!/bin/bash
start_human_count=$1
end_human_count=$2
start_vampire_count=$3
end_vampire_count=$4

echo "Executing sweep of Simulation with parameters: "
echo "  Initial Human Count -> " $start_human_count " to " $end_human_count
echo "  Initial Vampire Count -> " $start_vampire_count " to " $end_vampire_count

for human in `seq $start_human_count 1 $end_human_count`;
do
	for vampire in `seq $start_vampire_count 1 $end_vampire_count`;
    do
        sim_dir=bin/sim`date "+%Y-%m-%d_%H:%M:%S"`-h$human-v$vampire
        mkdir $sim_dir
        cp -r src/* $sim_dir
        cd $sim_dir

        if [ $# -eq 5 ]
        then
            dimension=$5
        else
            dimension=64x64
        fi

        python3 simulation.py $human $vampire 100 $dimension
        cd ../..
    done
done

echo "Completed sweep of Simulation"