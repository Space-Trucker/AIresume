#!/bin/bash
# Slow runs on the frozen copy of the reviewed code (git HEAD), sequential.
S=/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review
export PYTHONDONTWRITEBYTECODE=1
cd $S/frozen
run() {
  local d=$S/mutations/$1 t0=$(date +%s)
  python3 -I $S/scripts/run_ctx.py $d/goal.toml $2 $d/slowf.json --save-ctx $d/gt4ctx_f.json > $d/slowf.log 2>&1
  echo "$1 $2 done in $(( $(date +%s) - t0 ))s" >> $S/mutations/queue_f.log
}
for job in "baseline 4,8" "M37 4,8" "M45 4,8" "M12 4,8" "M11 4,8" "M09 4,8" "M39 4,8" "M38 4,8"; do run $job; done
echo ALLDONE >> $S/mutations/queue_f.log
