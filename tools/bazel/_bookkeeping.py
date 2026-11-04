"""Typed transport for native build selection and carry operations."""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(_ROOT/'hardware/scripts'))
import _rust_data
import _rust_part


def _json(value):
    if isinstance(value,Path):
        return str(value)
    if isinstance(value,dict):
        return {str(k):_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,set,frozenset)):
        return [_json(v) for v in value]
    return value


def call(op,*,callback=None,**fields):
    try:
        return _rust_data.request('build-data','bookkeeping-data',_json({'op':op,**fields}),callback=callback)
    except ValueError as exc:
        if 'SystemExit: ' in str(exc):
            raise SystemExit(str(exc).split('SystemExit: ',1)[1]) from None
        raise


def read(op,path,**fields):
    path=Path(path).resolve()
    try:
        _rust_part._READ_TARGETS.add(path.relative_to(_ROOT).as_posix())
    except ValueError:
        pass
    return call(op,path=str(path),**fields)
