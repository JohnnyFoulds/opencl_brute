#!/usr/bin/python3

import sys
import hashlib
from Library import opencl
from Library import zimcoin
from Library.opencl_information import opencl_information
from binascii import hexlify


def sha256_test(zimcoin_algo : zimcoin.zimcoin_algos, password_list : list):
    print("Testing Zimcoin ..")
    ctx = zimcoin_algo.cl_hash_init()
    cl_result = zimcoin_algo.cl_hash(ctx, password_list)
    
    for i, pwd in enumerate(password_list):
        print("Password: %s" % pwd)
        print("CL result      : %s" % hexlify(cl_result[i]))
        print("Correct result : %s" % hexlify(hashlib.sha256(pwd).digest()))
        print("")


def main(argv):
    if len(argv) < 2:
        print("Implementation tests")
        print("-----------------------------------------------------------------")
        info = opencl_information()
        info.printplatforms()
        print("\nPlease run as: python test_zimcoin.py [platform number]")
        return

    # Input values to be hashed
    password_list = [b'password', b'madness']

    platform = int(argv[1])
    debug = 0
    write_combined_file = True
    zimcoin_algos = zimcoin.zimcoin_algos(platform, debug, write_combined_file, inv_memory_density=1)

    sha256_test(zimcoin_algos, password_list)

    print("Tests have finished.")


if __name__ == '__main__':
    main(sys.argv)
