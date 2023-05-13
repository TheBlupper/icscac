#!/usr/bin/env python3
import subprocess
import os
import re
from pathlib import Path
from typing import Sequence, Union
from .generic import InstructionCounter

PathLike = Union[str, bytes, os.PathLike]

class PerfInstructionCounter(InstructionCounter):
    def __init__(self,
        target: PathLike):
        self.target = Path(target)

    def run_once(self, argv: Sequence[str] = (), stdin: Union[str, bytes] = '') -> int:
        if isinstance(stdin, str): stdin = stdin.encode()
        proc = subprocess.run(
            ['perf', 'stat', '-einstructions:u', '-x,',
            self.target.absolute(), *argv],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            input=stdin)
        m = re.search(b'(\d+),,instructions:u', proc.stderr)
        if m is None:
            raise ValueError(f'Got unexpected output from perf, instruction count missing: {proc.stderr}')
        return int(m.group(1))