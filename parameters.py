__version__ = "0.1.0"

import argparse
import configparser as cp
import sys
from typing import List, Union

import cadquery as cq
from helical_thread import HelicalThread, ThreadHelixes, helical_thread

from cq_bolt import cq_bolt
from utils import dbg, setCtx, show

setCtx(globals())

# Defaults

# Clearance between internal threads and external threads.
# The external threads are horzitionally moved to create
# the clearance.
DFLT_ext_clearance: float = 0.05

# Set to guarantee the thread and core overlap and a manifold is created
DFLT_thread_overlap: float = 0.001

# Tolerance value for generating STL files
DFLT_stl_tolerance: float = 1e-3

# The separation between edges of a helix after on revolution.
DFLT_pitch: float = 2

# The included angle of the "tip" of a thread
DFLT_angle_degs: float = 90

# Adjust z by inset so threads are inset from the bottom and top
DFLT_inset_offset: float = DFLT_pitch / 3

# The major diameter of outer most threads of nut,
# the minor diameter is the diameter of the inner most part of the nut
DFLT_dia_major: float = 8

# Height of main item
DFLT_height: float = 10 + (2 * DFLT_inset_offset)

# Size of the head
DFLT_head_size: float = 12

# Size of the flat at major diameter
DFLT_major_cutoff: float = DFLT_pitch / 8

# Size of the flat at minor diameter
DFLT_minor_cutoff: float = DFLT_pitch / 4

# A decimal fraction such that (taper_out_rpos * t_range) defines
# the t value where tapering out ends. The tapering begins at t: float = first_t.
DFLT_taper_out_rpos: float = 0.1

# A decimal fraction such that (taper_in_rpos * t_range) defines
# the t value where tapering in begins. The tapering ends at t: float = last_t.
DFLT_taper_in_rpos: float = 1 - DFLT_taper_out_rpos

# Height of head
DFLT_head_height = 4

# Amount substracted from bolt radius to hollow out the bolt
DFLT_wall_thickness = 2

class Parameters:
    version: str
    stl_tolerance: float
    dia_major: float
    head_size: float
    head_height: float
    wall_thickness: float
    ht: HelicalThread = HelicalThread(DFLT_dia_major / 2, DFLT_pitch, DFLT_height)

    def __init__(self, section: str, argv: List[str] = []):

        config = cp.ConfigParser()
        config.read("defaults.ini")

        self.version = __version__

        # Clearance between internal threads and external threads.
        # The external threads are horzitionally moved to create
        # the clearance.
        v = config.get(section, "ext_clearance", fallback=None)
        self.ht.ext_clearance = float(eval(v)) if v is not None else DFLT_ext_clearance

        # Set to guarantee the thread and core overlap and a manifold is created
        v = config.get(section, "thread_overlap", fallback=None)
        self.ht.thread_overlap = (
            float(eval(v)) if v is not None else DFLT_thread_overlap
        )

        # Tolerance value for generating STL files
        v = config.get(section, "stl_tolerance", fallback=None)
        self.stl_tolerance = float(eval(v)) if v is not None else DFLT_stl_tolerance

        # The separation between edges of a helix after on revolution.
        v = config.get(section, "pitch", fallback=None)
        self.ht.pitch = float(eval(v)) if v is not None else DFLT_pitch

        # The included angle of the "tip" of a thread
        v = config.get(section, "angle_degs", fallback=None)
        self.ht.angle_degs = float(eval(v)) if v is not None else DFLT_angle_degs

        # Adjust z by inset so threads are inset from the bottom and top
        v = config.get(section, "inset_offset", fallback=None)
        self.ht.inset_offset = float(eval(v)) if v is not None else DFLT_inset_offset

        # The major diameter of outer most threads of nut,
        # the minor diameter is the diameter of the inner most part of the nut
        v = config.get(section, "dia_major", fallback=None)
        self.dia_major = float(eval(v)) if v is not None else DFLT_dia_major
        self.ht.radius = self.dia_major / 2

        # Height of main item
        v = config.get(section, "height", fallback=None)
        self.ht.height = float(eval(v)) if v is not None else DFLT_height

        # Size of the head
        v = config.get(section, "head_size", fallback=None)
        self.head_size: float = float(eval(v)) if v is not None else DFLT_head_size

        # Size of the flat at major diameter
        v = config.get(section, "major_cutoff", fallback=None)
        self.ht.major_cutoff = float(eval(v)) if v is not None else DFLT_major_cutoff

        # Size of the flat at minor diameter
        v = config.get(section, "minor_cutoff", fallback=None)
        self.ht.minor_cutoff = float(eval(v)) if v is not None else DFLT_minor_cutoff

        # A decimal fraction such that (taper_out_rpos * t_range) defines
        # the t value where tapering out ends. The tapering begins at t = first_t.
        v = config.get(section, "taper_out_rpos", fallback=None)
        self.ht.taper_out_rpos = (
            float(eval(v)) if v is not None else DFLT_taper_out_rpos
        )

        # A decimal fraction such that (taper_in_rpos * t_range) defines
        # the t value where tapering in begins. The tapering ends at t = last_t.
        v = config.get(section, "taper_in_rpos", fallback=None)
        self.ht.taper_in_rpos = float(eval(v)) if v is not None else DFLT_taper_in_rpos

        # Height of head
        v = config.get(section, "head_height", fallback=None)
        self.head_height: float = float(eval(v)) if v is not None else DFLT_head_height

        # Amount substracted from bolt radius to hollow out the bolt
        v = config.get(section, "wall_thickness", fallback=None)
        self.wall_thickness: float = float(eval(v)) if v is not None else DFLT_wall_thickness

        parser: argparse.ArgumentParser = argparse.ArgumentParser(description=f"Create a {section} version={__version__}")

        parser.add_argument(
            "-v",
            "--version",
            help=f"Display version of {parser.prog} and exit",
            action="version",
            version=f"{__version__}",
        )
        parser.add_argument(
            "-st",
            "--stl_tolerance",
            help="stl file tollerance",
            nargs="?",
            type=float,
            default=self.stl_tolerance,
        )
        parser.add_argument(
            "-d",
            "--diameter",
            help="Diameter",
            nargs="?",
            type=float,
            default=self.dia_major,
        )
        parser.add_argument(
            "-c",
            "--ext_clearance",
            help="Clearance between internal and external threads",
            nargs="?",
            type=float,
            default=self.ht.ext_clearance,
        )
        parser.add_argument(
            "-to",
            "--thread_overlap",
            help="Thread overlap with core",
            nargs="?",
            type=float,
            default=self.ht.thread_overlap,
        )
        parser.add_argument(
            "-p",
            "--pitch",
            help="thread pitch",
            nargs="?",
            type=float,
            default=self.ht.pitch,
        )
        parser.add_argument(
            "-a",
            "--angle_degs",
            help="Angle of thread in degrees",
            nargs="?",
            type=float,
            default=self.ht.angle_degs,
        )
        parser.add_argument(
            "-in",
            "--inset_offset",
            help="Top and bottom inset of threads",
            nargs="?",
            type=float,
            default=self.ht.inset_offset,
        )
        parser.add_argument(
            "-he",
            "--height",
            help="Height of threads including inset",
            nargs="?",
            type=float,
            default=self.ht.height,
        )
        parser.add_argument(
            "-mj",
            "--major_cutoff",
            help="Thread cutoff at outside diameter (major_diameter)",
            nargs="?",
            type=float,
            default=self.ht.major_cutoff,
        )
        parser.add_argument(
            "-mi",
            "--minor_cutoff",
            help="Thread cutoff at inside diameter (minor_diameter)",
            nargs="?",
            type=float,
            default=self.ht.minor_cutoff,
        )
        parser.add_argument(
            "-tir",
            "--taper_in_rpos",
            help="Taper in relative position, so 0.1 is 10%% of the initial thread will be tapered",
            nargs="?",
            type=float,
            default=self.ht.taper_in_rpos,
        )
        parser.add_argument(
            "-tor",
            "--taper_out_rpos",
            help="Taper out relative position, so 0.9 means so 10%% of the ending portion of thread will be tapered",
            nargs="?",
            type=float,
            default=self.ht.taper_out_rpos,
        )
        parser.add_argument(
            "-hh",
            "--head_height",
            help="Head height",
            nargs="?",
            type=float,
            default=self.head_height,
        )
        parser.add_argument(
            "-hs",
            "--head_size",
            help="Size of head",
            nargs="?",
            type=float,
            default=self.head_size,
        )
        parser.add_argument(
            "-wt",
            "--wall_thickness",
            help="wall_thickness",
            nargs="?",
            type=float,
            default=self.wall_thickness,
        )

        args = parser.parse_args(argv)

        self.dia_major = args.diameter
        self.stl_tolerance = args.stl_tolerance
        self.head_height = args.head_height
        self.wall_thickness = args.wall_thickness

        self.ht.height = args.height
        self.ht.pitch = args.pitch
        self.ht.radius = self.dia_major / 2
        self.ht.angle_degs = args.angle_degs
        self.ht.inset_offset = args.inset_offset
        self.ht.ext_clearance = args.ext_clearance
        self.ht.taper_in_rpos = args.taper_in_rpos
        self.ht.taper_out_rpos = args.taper_out_rpos
        self.ht.major_cutoff = args.major_cutoff
        self.ht.minor_cutoff = args.minor_cutoff
        self.ht.thread_overlap = args.thread_overlap
