#!/bin/bash
S=/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review
export PYTHONDONTWRITEBYTECODE=1
cd $S/frozen
for m in baseline M28 M21 M43 M27 M49 M09 M39; do
  python3 -I $S/scripts/run_ctx.py $S/mutations/$m/goal.toml 5 $S/mutations/$m/gt5f.json > $S/mutations/$m/gt5f.log 2>&1
  echo "$m gt5 done" >> $S/mutations/gt5queue_f.log
done
echo GT5ALLDONE >> $S/mutations/gt5queue_f.log
