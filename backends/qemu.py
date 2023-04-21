import subprocess
import tempfile
import re
from pathlib import Path
import os
from typing import Sequence, Union
from .generic import InstructionCounter

PathLike = Union[str, bytes, os.PathLike]
class QemuInstructionCounter(InstructionCounter):
    def __init__(self,
        target: PathLike,
        qemu_binary: str,
        qemu_plugin: PathLike):
        self.target = Path(target)
        self.qemu_binary = qemu_binary
        self.qemu_plugin= Path(qemu_plugin)

    def run_once(self, arg: Sequence[str] = (), stdin: Union[str, bytes] = '') -> int:
        if isinstance(stdin, str): stdin = stdin.encode()
        proc = subprocess.run(
            [self.qemu_binary,
            '-plugin', f'{self.qemu_plugin.absolute()},inline=true',
            '-d', 'plugin',
            self.target.absolute(), arg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            input=stdin)
        
        return int(re.search(b'insns: (\d+)\n', proc.stderr).group(1))