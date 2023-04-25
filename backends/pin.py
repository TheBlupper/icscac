import subprocess
import tempfile
from pathlib import Path
import os
from typing import Sequence, Union
from .generic import InstructionCounter

PathLike = Union[str, bytes, os.PathLike]
REL_INSCOUNT_PATH = 'source/tools/ManualExamples/obj-{}/inscount1.so'

class PINInstructionCounter(InstructionCounter):
    def __init__(self,
        pin_path: PathLike,
        target_path: PathLike,
        arch:str = 'intel64'):
        self.pin_path = Path(pin_path)
        self.pin_binary_path = self.pin_path / 'pin'
        self.inscount_path = self.pin_path / REL_INSCOUNT_PATH.format(arch)
        self.target_path = Path(target_path)

    def run_once(self, args: Sequence[str] = (), stdin: Union[str, bytes] = '') -> int:
        if isinstance(stdin, str): stdin = stdin.encode()
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = subprocess.run(
                [self.pin_binary_path.absolute(),
                '-t', self.inscount_path.absolute(),
                '--', self.target_path.absolute(), *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=stdin,
                cwd=tmpdir)
            try:
                with open(Path(tmpdir)/'inscount.out', 'r') as outfile:
                    outfile.seek(6)
                    return int(outfile.read().strip())
            except Exception:
                raise ValueError(f'Pin failed, stdout + stderr: {proc.stdout + proc.stderr}')