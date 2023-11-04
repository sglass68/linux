#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0+
#
# Copyright 2023 Google LLC
# Written by Simon Glass <sjg@chromium.org>
#

"""Build a FIT containing a lot of devicetree files

Usage:
    make_fit.py -A arm64 -n 'Linux-6.6' -O linux
        -f arch/arm64/boot/image.fit -k /tmp/kern/arch/arm64/boot/image.itk
        /tmp/kern/arch/arm64/boot/dts/ -E -c gzip

Creates a FIT containing the supplied kernel and a directory containing the
devicetree files.

Use -E to generate an external FIT (where the data is placed after the
FIT data structure). This allows parsing of the data without loading
the entire FIT.

Use -c to compress the data, using bzip2, gzip, lz4, lzma, lzo and
zstd

The resulting FIT can be booted by bootloaders which support FIT, such
as U-Boot, Linuxboot, Tianocore, etc.

Note that this tool does not yet support adding a ramdisk / initrd.
"""

import argparse
import collections
import os
import re
import subprocess
import sys
import tempfile
import time

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
import libfdt


# Information about an EFL symbol:
# section (str): Name of the section containing this symbol
# address (int): Address of the symbol (its value)
# size (int): Size of the symbol in bytes
# weak (bool): True if the symbol is weak
# offset (int or None): Offset of the symbol's data in the ELF file, or None if
#   not known
Symbol = collections.namedtuple(
    'Symbol',
    ['section', 'address', 'size', 'weak', 'offset'])

# Tool extension and the name of the command-line tools
CompTool = collections.namedtuple('CompTool', 'ext,tools')

COMP_TOOLS = {
    'bzip2': CompTool('.bz2', 'bzip2'),
    'gzip': CompTool('.gz', 'pigz,gzip'),
    'lz4': CompTool('.lz4', 'lz4'),
    'lzma': CompTool('.lzma', 'lzma'),
    'lzo': CompTool('.lzo', 'lzop'),
    'zstd': CompTool('.zstd', 'zstd'),
}

def parse_args():
    """Parse the program ArgumentParser

    Returns:
        Namespace object containing the arguments
    """
    epilog = 'Build a FIT from a directory tree containing .dtb files'
    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument('-A', '--arch', type=str, required=True,
          help='Specifies the architecture')
    parser.add_argument('-c', '--compress', type=str, default='none',
          help='Specifies the compression')
    parser.add_argument('-E', '--external', action='store_true',
          help='Convert the FIT to use external data')
    parser.add_argument('-f', '--fit', type=str, required=True,
          help='Specifies the output file (.fit)')
    parser.add_argument('-k', '--kernel', type=str, required=True,
          help='Specifies the (uncompressed) kernel input file (.itk)')
    parser.add_argument('-n', '--name', type=str, required=True,
          help='Specifies the name')
    parser.add_argument('-O', '--os', type=str, required=True,
          help='Specifies the operating system')
    parser.add_argument('-V', '--vmlinux', type=str, required=True,
          help='Specifies the vmlinux output')
    parser.add_argument('srcdir', type=str, nargs='*',
          help='Specifies the directory tree that contains .dtb files')

    return parser.parse_args()

def setup_fit(fsw, name):
    """Make a start on writing the FIT

    Outputs the root properties and the 'images' node

    Args:
        fsw (libfdt.FdtSw): Object to use for writing
        name (str): Name of kernel image
    """
    fsw.INC_SIZE = 65536
    fsw.finish_reservemap()
    fsw.begin_node('')
    fsw.property_string('description', f'{name} with devicetree set')
    fsw.property_u32('#address-cells', 1)

    fsw.property_u32('timestamp', int(time.time()))
    fsw.begin_node('images')


def write_kernel(fsw, data, args, vbe_data):
    """Write out the kernel image

    Writes a kernel node along with the required properties

    Args:
        fsw (libfdt.FdtSw): Object to use for writing
        data (bytes): Data to write (possibly compressed)
        args (Namespace): Contains necessary strings:
            arch: FIT architecture, e.g. 'arm64'
            fit_os: Operating Systems, e.g. 'linux'
            name: Name of OS, e.g. 'Linux-6.6.0-rc7'
            compress: Compression algorithm to use, e.g. 'gzip'
        vbe_data (bytes): VBE bytestring from kernel
    """
    with fsw.add_node('kernel'):
        fsw.property_string('description', args.name)
        fsw.property_string('type', 'kernel_noload')
        fsw.property_string('arch', args.arch)
        fsw.property_string('os', args.os)
        fsw.property_string('compression', args.compress)
        fsw.property('data', data)
        fsw.property_u32('load', 0)
        fsw.property_u32('entry', 0)

        if vbe_data:
            for item in vbe_data[:-1].split(b'\0'):
                compat = item.decode('utf-8')
                vbe, name = compat.split(',')
                with fsw.add_node(name):
                    fsw.property_string('compatible', compat)


def finish_fit(fsw, entries):
    """Finish the FIT ready for use

    Writes the /configurations node and subnodes

    Args:
        fsw (libfdt.FdtSw): Object to use for writing
        entries (list of tuple): List of configurations:
            str: Description of model
            str: Compatible stringlist
    """
    fsw.end_node()
    seq = 0
    with fsw.add_node('configurations'):
        for model, compat in entries:
            seq += 1
            with fsw.add_node(f'conf-{seq}'):
                fsw.property('compatible', bytes(compat))
                fsw.property_string('description', model)
                fsw.property_string('fdt', f'fdt-{seq}')
                fsw.property_string('kernel', 'kernel')
    fsw.end_node()


def compress_data(inf, compress):
    """Compress data using a selected algorithm

    Args:
        inf (IOBase): Filename containing the data to compress
        compress (str): Compression algorithm, e.g. 'gzip'

    Return:
        bytes: Compressed data
    """
    if compress == 'none':
        return inf.read()

    comp = COMP_TOOLS.get(compress)
    if not comp:
        raise ValueError(f"Unknown compression algorithm '{compress}'")

    with tempfile.NamedTemporaryFile() as comp_fname:
        with open(comp_fname.name, 'wb') as outf:
            done = False
            for tool in comp.tools.split(','):
                try:
                    subprocess.call([tool, '-c'], stdin=inf, stdout=outf)
                    done = True
                    break
                except FileNotFoundError:
                    pass
            if not done:
                raise ValueError(f'Missing tool(s): {comp.tools}\n')
            with open(comp_fname.name, 'rb') as compf:
                comp_data = compf.read()
    return comp_data


def output_dtb(fsw, seq, fname, arch, compress):
    """Write out a single devicetree to the FIT

    Args:
        fsw (libfdt.FdtSw): Object to use for writing
        seq (int): Sequence number (1 for first)
        fmame (str): Filename containing the DTB
        arch: FIT architecture, e.g. 'arm64'
        compress (str): Compressed algorithm, e.g. 'gzip'

    Returns:
        tuple:
            str: Model name
            bytes: Compatible stringlist
    """
    with fsw.add_node(f'fdt-{seq}'):
        # Get the compatible / model information
        with open(fname, 'rb') as inf:
            data = inf.read()
        fdt = libfdt.FdtRo(data)
        model = fdt.getprop(0, 'model').as_str()
        compat = fdt.getprop(0, 'compatible')

        fsw.property_string('description', model)
        fsw.property_string('type', 'flat_dt')
        fsw.property_string('arch', arch)
        fsw.property_string('compression', compress)
        fsw.property('compatible', bytes(compat))

        with open(fname, 'rb') as inf:
            compressed = compress_data(inf, compress)
        fsw.property('data', compressed)
    return model, compat


def build_fit(args, vbe_data):
    """Build the FIT from the provided files and arguments

    Args:
        args (Namespace): Program arguments
        vbe_data (bytes): VBE bytestring from kernel

    Returns:
        tuple:
            bytes: FIT data
            int: Number of configurations generated
            size: Total uncompressed size of data
    """
    fsw = libfdt.FdtSw()
    setup_fit(fsw, args.name)
    seq = 0
    size = 0
    entries = []

    # Handle the kernel
    with open(args.kernel, 'rb') as inf:
        comp_data = compress_data(inf, args.compress)
    size += os.path.getsize(args.kernel)
    write_kernel(fsw, comp_data, args, vbe_data)

    for path in args.srcdir:
        # Handle devicetree files
        if os.path.isdir(path):
            for dirpath, _, fnames in os.walk(path):
                for fname in fnames:
                    if os.path.splitext(fname)[1] != '.dtb':
                        continue
                    pathname = os.path.join(dirpath, fname)
                    seq += 1
                    size += os.path.getsize(pathname)
                    model, compat = output_dtb(fsw, seq, pathname,
                                               args.arch, args.compress)
                    entries.append([model, compat])

    finish_fit(fsw, entries)

    # Include the kernel itself in the returned file count
    return fsw.as_fdt().as_bytearray(), seq + 1, size


def _get_file_offset(elf, addr):
    """Get the file offset for an address

    Args:
        elf (ELFFile): ELF file to check
        addr (int): Address to search for

    Returns
        int: Offset of that address in the ELF file, or None if not valid
    """
    for seg in elf.iter_segments():
        seg_end = seg['p_vaddr'] + seg['p_filesz']
        if seg.header['p_type'] == 'PT_LOAD':
            if addr >= seg['p_vaddr'] and addr < seg_end:
                return addr - seg['p_vaddr'] + seg['p_offset']

def get_sym_file_offset(fname, patterns):
    """Get the symbols from an ELF file

    Args:
        fname: Filename of the ELF file to read
        patterns: List of regex patterns to search for, each a string

    Returns:
        None, if the file does not exist, or Dict:
          key: Name of symbol
          value: Hex value of symbol
    """
    syms = {}
    with open(fname, 'rb') as inf:
        elf = ELFFile(inf)

        re_syms = re.compile('|'.join(patterns))
        for section in elf.iter_sections():
            if isinstance(section, SymbolTableSection):
                for symbol in section.iter_symbols():
                    if not re_syms or re_syms.search(symbol.name):
                        addr = symbol.entry['st_value']
                        syms[symbol.name] = Symbol(
                            section.name, addr, symbol.entry['st_size'],
                            symbol.entry['st_info']['bind'] == 'STB_WEAK',
                            _get_file_offset(elf, addr))

    # Sort dict by address
    return collections.OrderedDict(
        sorted(syms.items(), key=lambda x: x[1].address))


def decode_vbe(fname):
    """Read the required VBE parameters from the Linux ELF file

    Args:
        fname (str): Filename to read
    """
    syms = get_sym_file_offset(fname, ['__vbe_'])

    start = syms['__vbe_start'].offset
    size = syms['__vbe_end'].offset - start
    with open(fname, 'rb') as inf:
        inf.seek(start)
        vbe_data = inf.read(size)
    return vbe_data


def run_make_fit():
    """Run the tool's main logic"""
    args = parse_args()

    vbe_data = decode_vbe(args.vmlinux) if args.vmlinux else None

    out_data, count, size = build_fit(args, vbe_data)
    with open(args.fit, 'wb') as outf:
        outf.write(out_data)

    ext_fit_size = None
    if args.external:
        mkimage = os.environ.get('MKIMAGE', 'mkimage')
        subprocess.check_call([mkimage, '-E', '-F', args.fit],
                              stdout=subprocess.DEVNULL)

        with open(args.fit, 'rb') as inf:
            data = inf.read()
        ext_fit = libfdt.FdtRo(data)
        ext_fit_size = ext_fit.totalsize()

    comp_size = len(out_data)
    print(f'FIT size {comp_size:#x}/{comp_size / 1024 / 1024:.1f} MB', end='')
    if ext_fit_size:
        print(f', header {ext_fit_size:#x}/{ext_fit_size / 1024:.1f} KB', end='')
    print(f', {count} files, uncompressed {size / 1024 / 1024:.1f} MB')


if __name__ == "__main__":
    sys.exit(run_make_fit())
