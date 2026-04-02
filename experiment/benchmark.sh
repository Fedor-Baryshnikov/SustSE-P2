#!/bin/bash
set -e  

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results_comparison"

ENERGIBRIDGE="/usr/local/bin/energibridge"

mkdir -p "$RESULTS_DIR"

OLLAMA_PID=$(pgrep -x ollama || true)
if [ -z "$OLLAMA_PID" ]; then
    echo "Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    echo "Ollama PID: $OLLAMA_PID"
    sleep 5
else
    echo "Ollama already running, PID=$OLLAMA_PID"
fi

runs=()
for i in {1..1}; do runs+=("strategy1"); done
for i in {1..1}; do runs+=("strategy2"); done

for ((i=${#runs[@]}-1; i>0; i--)); do
    j=$((RANDOM % (i+1)))
    tmp=${runs[i]}
    runs[i]=${runs[j]}
    runs[j]=$tmp
done

s1_count=0
s2_count=0
run_number=0
total_runs=${#runs[@]}

for label in "${runs[@]}"; do
    run_number=$((run_number + 1))

    if [ "$label" = "strategy1" ]; then
        s1_count=$((s1_count + 1))
        count=$s1_count
        script="$SCRIPT_DIR/strategy1.py"
    else
        s2_count=$((s2_count + 1))
        count=$s2_count
        script="$SCRIPT_DIR/strategy2.py"
    fi

    output_prefix="$RESULTS_DIR/${label}_run${count}"
    output_csv="${output_prefix}.csv"

    echo "RUN $run_number/$total_runs, Strategy=$label Run#$count"

    sudo "$ENERGIBRIDGE" --output "$output_csv" --gpu -- "$(which python)" "$script" "$output_prefix"

    echo "Run $run_number complete. Results saved to $output_prefix*"
done

echo "All runs finished, Results saved to: $RESULTS_DIR"

echo "Analyzing..."
python "$SCRIPT_DIR/analyze_results.py"
