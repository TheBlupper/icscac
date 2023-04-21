#!/usr/bin/env python3
from typing import Sequence, Union, Iterable
from multiprocessing import Pool

class InstructionCounter:
    def run_once(self, arg: Sequence[str] = (), stdin: Union[str, bytes] = '') -> int:
        raise NotImplementedError()
    
    def _run_once_wrapper(self, inp):
        '''For use in multiprocessing'''
        proc_id, args, stdin = inp
        return proc_id, self.run_once(args, stdin)
    
    def run_parallel(self,
            args: Sequence[str] = None,
            stdins: Sequence[str] = None,
            proc_count: int = 10) -> Iterable[int]:
        '''
        Runs several processes in parallel using multiprocessing. Return values
        are guaranteed to be in the same order as inputs.
        '''
        
        if args is not None and stdins is None:
            stdins = ['']*len(args)
        elif args is None and stdins is not None:
            args = ['']*len(stdins)
        elif args is None and stdins is None: # None provided
            raise ValueError('Provide at least one of argss and stdins')
        else: # Both provided
            if len(args) != len(stdins):
                raise ValueError('Length mismatch between argss and stdins')
            
        # imap_unordered is only marginally faster and
        # makes things more cumbersome
        for proc_id, instr_count in Pool(proc_count).imap(
            self._run_once_wrapper,
            zip(range(len(args)), args, stdins)
        ):
            yield instr_count  