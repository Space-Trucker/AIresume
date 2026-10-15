#!/bin/bash
# Sequential slow runs: GT-4 (+GT-8 on its context) and GT-5, through run_ctx.py
S=/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review
R="python3 -I $S/scripts/run_ctx.py"
export PYTHONDONTWRITEBYTECODE=1
cd /home/user/AIresume/trading/goal
run() { # id tests outname
  local d=$S/mutations/$1
  local t0=$(date +%s)
  $R $d/goal.toml $2 $d/$3 --save-ctx $d/gt4ctx_$3 > $d/$3.log 2>&1
  echo "$1 $2 $3 done in $(( $(date +%s) - t0 ))s" >> $S/mutations/queue.log
}
run baseline 4,5,8 slow.json
run M11 4,8 slow.json
run M12 4,8 slow.json
run M09 4,5,8 slow.json
run M45 4,8 slow.json
run M37 4,8 slow.json
run M28 5 slow.json
run M21 5 slow.json
run M43 5 slow.json
run M27 5 slow.json
run M49 5 slow.json
run M39 4,5,8 slow.json
run M38 4,8 slow.json
echo ALLDONE >> $S/mutations/queue.log
