#!/bin/sh
cd /home/user/AIresume/trading/goal
python3 -m goaltests "$1" --only 4,8 > "$2" 2>&1
grep -E "G1 passes|G2 passes|best of|reaches real money|share passing|probability|program" "$2" | cut -c1-330
