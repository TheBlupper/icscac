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

    def run_once(self, arg: Sequence[str] = (), stdin: Union[str, bytes] = '') -> int:
        if isinstance(stdin, str): stdin = stdin.encode()
        proc = subprocess.run(
            ['perf', 'stat', '-einstructions:u', '-x,',
            self.target.absolute(), arg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            input=stdin)
        return int(re.search(b'(\d+),,instructions:u', proc.stderr).group(1))