#!/usr/bin/python3

import sys
import hashlib
from Library import opencl
from Library.opencl_information import opencl_information
from binascii import hexlify


def sha256_test(opencl_algo : opencl.opencl_algos, password_list : list):
    print("Testing sha256 ..")
    ctx = opencl_algo.cl_sha256_init()
    cl_result = opencl_algo.cl_sha256(ctx, password_list)
    
    for i, pwd in enumerate(password_list):
        print("Password: %s" % pwd)
        print("CL result      : %s" % hexlify(cl_result[i]))
        print("Correct result : %s" % hexlify(hashlib.sha256(pwd).digest()))
        print("")

def long_test(opencl_algo : opencl.opencl_algos, window_size : int = 100000000):
    # create the password list
    password_list = []
    # 10000000
    for i in range(0, window_size):
        password_list.append(b'password' + str(i).encode('utf-8'))
    
    ctx = opencl_algo.cl_sha256_init()
    cl_result = opencl_algo.cl_sha256(ctx, password_list)

    # for i, pwd in enumerate(password_list):
    #     hashlib.sha256(pwd).digest()
    #     print("Password: %s" % pwd)
    #     print("CL result      : %s" % hexlify(cl_result[i]))
    #     print("Correct result : %s" % hexlify(hashlib.sha256(pwd).digest()))
    #     print("")

def main(argv):
    if len(argv) < 2:
        print("Implementation tests")
        print("-----------------------------------------------------------------")
        info = opencl_information()
        info.printplatforms()
        print("\nPlease run as: python test.py [platform number]")
        return

    # Input values to be hashed
    password_list = [b'password', b'madness']

    platform = int(argv[1])
    debug = 0
    write_combined_file = True
    opencl_algos = opencl.opencl_algos(platform, debug, write_combined_file, inv_memory_density=1)

    #print("============ Initial Test ================")
    #sha256_test(opencl_algos, password_list)

    print("============== Long Test =================")
    long_test(opencl_algos)

    print("Tests have finished.")


if __name__ == '__main__':
    main(sys.argv)
