import sys
from Library import opencl
from Library.opencl_information import opencl_information


def sha256_hash_test(opencl_algo : opencl.opencl_algos, plaintext : str):
    """
    Test the SHA256 hashing function.
    """
    ctx = opencl_algo.cl_sha256_init()
    ctx,
    #clresult = opencl_algo.cl_sha256(ctx, passwordlist)

    print("\nTest SHA256 Hashing")
    print("-----------------------------------------------------------------")
    print("Plaintext: ", plaintext)
    #print("Hash: ", opencl_algo.sha256_hash(plaintext))
    print("-----------------------------------------------------------------")
    print("\n")


def main(argv):
    """
    The main function that is executed when the test is run.
    """
    if len(argv) < 2:
        print("Test SHA256 Hashing")
        print("-----------------------------------------------------------------")
        info = opencl_information()
        info.printplatforms()
        print("\nPlease run as: python sha256_test.py [platform number]")
        return

    # get the algorithms
    platform = int(argv[1])
    debug = 0
    write_combined_file = False

    opencl_algos = opencl.opencl_algos(
        platform, debug, write_combined_file, inv_memory_density=1)

    # test the SHA256 hashing function
    sha256_hash_test(opencl_algos, "Hello World!")


if __name__ == '__main__':
    main(sys.argv)