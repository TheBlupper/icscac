#!/usr/bin/env python3
import argparse
import os
import string
from pathlib import Path
from .backends.pin import PINInstructionCounter
from .backends.perf import PerfInstructionCounter
from .backends.qemu import QemuInstructionCounter

def main():
    parser = argparse.ArgumentParser(
        prog='scac',
        description='Pre-made helper functions to analyze side-channels.')
    
    parser.add_argument('target', type=str,
                        help='target program to analyze')
    
    search_mode_group = parser.add_mutually_exclusive_group(required=True)
    search_mode_group.add_argument('--stdin',
        action='store_const',
        const='stdin',
        dest='input_mode',
        help='Send input via stdin')
    search_mode_group.add_argument('--arg', 
        action='store_const',
        const='arg',
        dest='input_mode',
        help='Send input via argv[2]')

    search_mode_group = parser.add_mutually_exclusive_group(required=True)
    search_mode_group.add_argument('--brute-length', 
        action='store_const',
        const='brute-length',
        dest='search_mode',
        help='Find the best length of input')
    
    search_mode_group.add_argument('--brute-forward', 
        action='store_const',
        const='brute-forward',
        dest='search_mode',
        help='Brute input from the start of the string')
    
    search_mode_group.add_argument('--brute-backward', 
        action='store_const',
        const='brute-backward',
        dest='search_mode',
        help='Brute input from the end of the string')
    
    search_mode_group.add_argument('--brute-all', 
        action='store_const',
        const='brute-all',
        dest='search_mode',
        help='Brute one character at a time at all possible positions')
    
    parser.add_argument('-b', '--backend',
        choices=['perf', 'pin', 'qemu'],
        default='perf',
        help='''Instruction-counting backend to use.
                Pin is more exact, perf is much faster, qemu is mid.''')
    
    parser.add_argument('--arch', type=str,
        default='intel64',
        help='''Architure to use, usually intel64 or ia32.
        Only applicable for the PIN backend''')

    parser.add_argument('--pin', type=str,
        default=(Path(__file__)/'pin').absolute(),
        help='''Path to pin folder (not the binary).
        Only applicable for the PIN backend''')
    
    parser.add_argument('--qemu-binary', type=str,
        default='qemu-x86_64',
        help='''Name or path to the appropriate qemu usermode binary.
        Only applicable for the qemu backend''')
    
    parser.add_argument('--qemu-plugin', type=str,
        default=(Path(__file__).parent/'libinsn.so').absolute(),
        help='''Path to libinsn.so.
        Only applicable for the qemu backend''')
    
    parser.add_argument('-p', '--prefix', type=str,
                        default='',
                        help='Prefix for program input')
    
    parser.add_argument('-s', '--suffix', type=str,
                        default='',
                        help='Suffix for program input')
    
    parser.add_argument('-a', '--alph', type=str,
                        default=string.printable.strip(),
                        help='Possible input characters')

    parser.add_argument('-t', '--tmpchar', type=str,
                        default='A',
                        help='Temporary character to use to fill out the input')
    
    parser.add_argument('-l', '--length', type=int,
                        default=32,
                        help='Length of input to try, or maximum length when in length mode')
    
    parser.add_argument('--procs', type=int,
                        default=15,
                        help='Amount of processes to use when multiprocessing')
    args = parser.parse_args()
    args.prefix = args.prefix.replace('\\n', '\n')
    args.suffix = args.suffix.replace('\\n', '\n')

    target_path = Path(args.target)
    if not os.path.isfile(target_path):
        raise ValueError('Target program does not exist')

    if args.backend == 'pin':
        pin_path = Path(args.pin)
        if not os.path.isfile(pin_path/'pin'):
            raise ValueError('Pin path does not contain a "pin" binary!')
        
        instr_counter = PINInstructionCounter(pin_path, target_path, args.arch)
    elif args.backend == 'perf':
        instr_counter = PerfInstructionCounter(args.target)
    elif args.backend == 'qemu':
        instr_counter = QemuInstructionCounter(args.target, args.qemu_binary, args.qemu_plugin)

    def run_inputs(inputs):

        if args.input_mode == 'stdin':
            inputs = [args.prefix + inp + args.suffix
                for inp in inputs]
        elif args.input_mode == 'arg':
            prefix = [args.prefix] if args.prefix else []
            suffix = [args.suffix] if args.suffix else []
            inputs = [prefix + [inp] + suffix
                for inp in inputs]
                
        run_parallel_args = {
            'argss' if args.input_mode=='arg' else 'stdins': inputs,
            'proc_count': args.procs
        }
        yield from instr_counter.run_parallel(**run_parallel_args)
        
    if args.search_mode == 'brute-length':
        brute_length(args.length, run_inputs, args.tmpchar)
    if args.search_mode == 'brute-all':
        brute_all(args.alph, args.length, run_inputs, args.tmpchar)
    if args.search_mode == 'brute-forward':
        brute_forward(args.alph, args.length, run_inputs, args.tmpchar)
    if args.search_mode == 'brute-backward':
        brute_backward(args.alph, args.length, run_inputs, args.tmpchar)

def brute_length(max_length, run_inputs, tmp_char):
    inputs = [tmp_char*i for i in range(max_length)]
    outputs = []
    for length, inscount in enumerate(run_inputs(inputs)):
        outputs += [inscount]
        print(f'{length=} {inscount=}')
    most_instrs = max(outputs)
    best_length = outputs.index(most_instrs)
    print(f'{most_instrs=} {best_length=}')

def brute_backward(alph, length, run_inputs, tmp_char):
    found = ''
    while len(found) < length:
        inputs = []
        for ch in alph:
            inputs.append(tmp_char*(length-len(found)-1) + ch + found)
        outputs = []
        for i, inscount in enumerate(run_inputs(inputs)):
            print(f'{inscount=} {inputs[i]!r}')
            outputs.append(inscount)
        best = max(outputs)
        found = alph[outputs.index(best)] + found
    print(f'found input {found}')

def brute_forward(alph, length, run_inputs, tmp_char):
    found = ''
    while len(found) < length:
        inputs = []
        for ch in alph:
            inputs.append(found + ch + tmp_char*(length-len(found)-1))
        outputs = []
        for i, inscount in enumerate(run_inputs(inputs)):
            print(f'{inscount=} {inputs[i]!r}')
            outputs.append(inscount)
        best = max(outputs)
        found += alph[outputs.index(best)]
    print(f'found input {found}')

def brute_all(alph, length, run_inputs, tmp_char):
    found = [None]*length
    while None in found:
        inputs = []
        input_lut = []
        for idx in range(length):
            if found[idx] != None: continue
            for ch in alph:
                input_lut.append((idx, ch))
                inputs.append(
                    ''.join(ch if i==idx else (tmp_char if found[i] is None else found[i]) for i in range(length))
                )
        outputs = []
        for i, instr_count in enumerate(run_inputs(inputs)):
            print(f'{instr_count=} {inputs[i]!r}')
            outputs.append(instr_count)
        best = max(outputs)
        best_idx, best_char = input_lut[outputs.index(best)]
        found[best_idx] = best_char
        print(f'\n{best_idx=} {best_char=}')
    print(f'found input {"".join(found)}')

if __name__ == '__main__':
    main()