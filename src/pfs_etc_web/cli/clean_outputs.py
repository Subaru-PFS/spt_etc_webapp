#!/usr/bin/env python3

import argparse
import os


def get_arguments():
    parser = argparse.ArgumentParser(description="Clean output files in a folder")
    parser.add_argment("dir", type=str, help="directory to be cleaned")

    args = parser.parse_args()

    return args


def main():
    args = get_arguments()

    pass


if __name__ == "__main__":
    main()
