#!/usr/bin/python2
# -*- coding: utf-8 -*-

from grap_disassembler import disassembler
import subprocess
import os

GRAP_VERSION="0.6.8"

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='grap: look for pattern in a PE/ELF binary or a .dot graph file')
    parser.add_argument('--version', action='version', version=GRAP_VERSION)

    parser.add_argument(dest='pattern',  help='Pattern file (.dot) to look for')
    parser.add_argument(dest='test', nargs="+", help='Test file(s) to analyse')

    parser.add_argument('-f', '--force', dest='force', action="store_true", default=False, help='Force re-generation of existing .dot file')
    parser.add_argument('-o', '--dot-output', dest='dot', help='Specify exported .dot file name')
    parser.add_argument('-r', '--readable', dest='readable', action="store_true", default=False, help='DOT in displayable format (with xdot)')
    parser.add_argument('-od', '--only-disassemble', dest='only_disassemble', action="store_true", default=False, help='Disassemble files and exit (no matching)')
    parser.add_argument('-m', '--print-all-matches', dest='print_all_matches', action="store_true", default=False, help='Print all matched nodes (overrides getid fields)')
    parser.add_argument('-nm', '--print-no-matches', dest='print_no_matches', action="store_true", default=False, help='Don\'t print matched nodes (overrides getid fields)')
    parser.add_argument('-sa', '--show-all', dest='show_all', action="store_true", default=False, help='show all tested files (not default when quiet, default otherwise)')
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False, help='Verbose output')
    parser.add_argument('-d', '--debug', dest='debug', action="store_true", default=False, help='Debug output')
    parser.add_argument('-q', '--quiet', dest='quiet', action="store_true", default=False, help='Quiet output')
    args = parser.parse_args()

    printed_something = False

    if args.pattern is None or args.test is None:
        sys.exit(0)

    if args.dot is not None and len(args.test) > 1:
        print("You can specify dot path only when there is one test file.")
        sys.exit(0)

    dot_test_files = []
    for test_path in args.test:
        data = open(test_path, "r").read()
        if data is None:
            print("Can't open test file " + test_path)
            sys.exit(0)

        if data[0:7].lower() == "digraph":
            dot_test_files.append(test_path)
        else:
            if args.dot is None:
                dotpath = test_path + ".dot"
            else:
                dotpath = args.dot

            if os.path.exists(dotpath) and not args.force:
                if args.verbose:
                    print("Skipping generation of existing " + dotpath)
                    printed_something = True
                dot_test_files.append(dotpath)
            else:
                if data[0:2] == "MZ":
                    disassembler.disassemble_pe(test_path, dotpath, print_listing=False, readable=False, verbose=False)
                    dot_test_files.append(dotpath)
                elif data[0:4] == "\x7fELF":
                    disassembler.disassemble_elf(test_path, dotpath, print_listing=False, readable=False, verbose=False)
                    dot_test_files.append(dotpath)
                else:
                    if args.verbose:
                        print("Test file " + test_path + " does not seem to be a PE/ELF or dot file.")
                        printed_something = True

    if not args.only_disassemble:
        if args.pattern is not None and len(dot_test_files) >= 1:
            if printed_something or args.verbose:
                print("")
            command = ["/usr/local/bin/grap-match"]

            if args.print_all_matches:
                command.append("-m")

            if args.print_no_matches:
                command.append("-nm")

            if args.verbose:
                command.append("-v")

            if args.debug:
                command.append("-d")

            if args.quiet:
                command.append("-q")

            if args.show_all:
                command.append("-sa")

            command.append(args.pattern)

            for test_path in dot_test_files:
                command.append(test_path)

            if args.verbose or args.debug:
                print(" ".join(command))

            popen = subprocess.Popen(tuple(command))
            popen.wait()
        else:
            if not args.quiet:
                print("Missing pattern or test file.")

