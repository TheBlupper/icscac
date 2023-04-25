# Instruction Counting Side Channel Analysis Cheese

A Python script inspired by https://github.com/ChrisTheCoolHut/PinCTF and the like.

It provides easy to use methods of side-channel analysis of binaries by counting instructions. It offers three backends: `perf`, `pin` and `qemu`. `pin` uses the Intel PIN framework and gives very exact but very slow results. For most binaries the small inaccuracies of `perf` will not have an effect on the result. `qemu` is often the best of two worlds with much better performance than `pin` and very exact results.

## Example:

## **Just the Check Please** from PlaidCTF 2023
python3 -m icscac --arg --brute-length -- ./icscac/examples/check @@
```
length=0 inscount=255635
length=1 inscount=255685
length=2 inscount=255365
...
length=15 inscount=255413
length=16 inscount=30191787
length=17 inscount=255486
...
length=31 inscount=255880
most_instrs=30191787 best_length=16
```

python3 -m icscac --arg --brute-all -l 16 -- ./icscac/examples/check @@
```
instr_count=30191457 '0AAAAAAAAAAAAAAA'
instr_count=30191346 '1AAAAAAAAAAAAAAA'
instr_count=30192062 '2AAAAAAAAAAAAAAA'
...
instr_count=40089999 'wat3rT1ghT-bl}z3'
instr_count=40090186 'wat3rT1ghT-bl~z3'

best_idx=13 best_char='A'
found input wat3rT1ghT-blAz3
```