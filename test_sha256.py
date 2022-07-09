#!/usr/bin/python3

import sys
import hashlib
from Library import opencl
from Library.opencl_information import opencl_information
from binascii import hexlify


def sha256_test(opencl_algo, passwordlist):
    print("Testing sha256 ..")
    ctx = opencl_algo.cl_sha256_init()
    clresult = opencl_algo.cl_sha256(ctx, passwordlist)
    
    for i, pwd in enumerate(passwordlist):
        print("Password: %s" % pwd)
        print("CL result      : %s" % hexlify(clresult[i]))
        print("Correct result : %s" % hexlify(hashlib.sha256(pwd).digest()))
        print("")


def main(argv):
    if len(argv) < 2:
        print("Implementation tests")
        print("-----------------------------------------------------------------")
        info = opencl_information()
        info.printplatforms()
        print("\nPlease run as: python test.py [platform number]")
        return

    # Input values to be hashed
    passwordlist = [b'password', b'hmm', b'trolololl', b'madness']

    platform = int(argv[1])
    debug = 0
    write_combined_file = False
    opencl_algos = opencl.opencl_algos(platform, debug, write_combined_file, inv_memory_density=1)

    sha256_test(opencl_algos, passwordlist)

    print("Tests have finished.")


if __name__ == '__main__':
    main(sys.argv)
