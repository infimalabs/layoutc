"""Encode multiple speedball layouts into one atlas.

This tool reads and writes PNG, JSON, and TSV layouts representing spatial entities.
PNG representations are created by encoding the spatial entities as RGBA pixels. JSON
representations are created by encoding the spatial entities as a list of dictionaries.
TSV representations are created by encoding the spatial entities as a list of tabular
rows. The tool can convert between these representations and encode them at different
color depths and pixel pitches.
"""

import sys, argparse

from . import Depth, Pitch
from .codec import Codec
from .entity import Entity
# Registers entity formats.
from .entity import json as _
from .entity import png as _


try:
    VERSION = __import__("importlib.metadata").metadata.version(__package__)
except ImportError:
    VERSION = "0.0.0"
finally:
    SOFTWARE = f"{__package__} {VERSION} (Python {sys.version.split()[0]})"


class Namespace(argparse.Namespace):

    verbose: bool

    depth: Depth
    pitch: Pitch

    from_: type[Entity]|None
    input: list[str]

    into: type[Entity]|None
    output: str


def command(ns:Namespace):
    codec = Codec(depth=ns.depth, pitch=ns.pitch)
    if len(ns.input) > 1:
        ns.input, ns.output = ns.input[:-1], ns.input[-1]
    for name in ns.input:
        with sys.stdin.buffer if name == "-" else open(name, 'rb') as fp:
            codec.load(fp, ns.from_)
    with sys.stdout.buffer if ns.output == "-" else open(ns.output, 'wb') as fp:
        codec.dump(fp, ns.into)


def depth(s:str):
    return Depth[s.upper()] if s.upper() in Depth.__members__ else Depth(int(s))


def pitch(s:str):
    return Pitch[s.upper()] if s.upper() in Pitch.__members__ else Pitch(int(s))


def entity(s:str):
    return __import__(s if "." in s else f"{Entity.__module__}.{s}", fromlist=['']).Entity


def main(parser:type[argparse.ArgumentParser]=argparse.ArgumentParser, name=__package__, description=__doc__):
    parser = parser(name, description=description, epilog=SOFTWARE)
    parser.add_argument('input', nargs='*', help='input layouts (default: %(default)s)', type=str, default="-")
    parser.add_argument('output', nargs='?', help='output layout (default: %(default)s)', type=str, default='-')
    parser.add_argument('-v', '--verbose', help='show verbose traceback on error', action='store_true')
    parser.add_argument('--depth', help='color depth (default: %(default)s color)', type=depth, choices=Depth, default=Depth.HIRES)
    parser.add_argument('--pitch', help='pixel pitch (default: %(default)s mm/px)', type=pitch, choices=Pitch, default=Pitch.LORES)
    parser.add_argument('--from', help='from entity (default: per contents)', type=entity, metavar='ENTITY', dest='from_')
    parser.add_argument('--into', help='into entity (default: per filename)', type=entity, metavar='ENTITY')
    ns = Namespace()
    try:
        parser.parse_args(namespace=ns)
    except Exception as e:
        if ns.verbose: raise
        parser.error(str(e))
    try:
        statmsg = command(ns)
    except KeyboardInterrupt as e:
        if ns.verbose: raise
        parser.exit(130)
    except BrokenPipeError as e:
        if ns.verbose: raise
        parser.exit(141)
    except Exception as e:
        if ns.verbose: raise
        parser.exit(1, f"error: {e}\n")
    match statmsg:
        case 0|None:
            parser.exit(0)
        case status, ""|None:
            parser.exit(status)
        case status, message if isinstance(message, str):
            parser.exit(status, f"{message.strip()}\n")
        case _ if isinstance(statmsg, str):
            parser.exit(1, f"{statmsg.strip()}\n")
        case _ if isinstance(statmsg, int):
            parser.exit(statmsg, f"error: exit {statmsg}\n")
        case _:
            parser.exit(1, f"error: {statmsg = !r}\n")


if __name__ == '__main__':
    main()
