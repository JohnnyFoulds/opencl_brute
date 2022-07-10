import numpy as np
import pyopencl as cl
from Library import opencl
from Library.buffer_structs import buffer_structs
from Library.opencl import concat, mdpad_64_func

class zimcoin_interface(opencl.opencl_interface):
    """
    Provide custom functions for zimcoin tests and mining.
    """
    def __init__(self, platformNum, debug=0, write_combined_file=False,
                maxWorkgroupSize=60000, inv_memory_density=1,
                 N_value=15, openclDevice = 0):
        super().__init__(platformNum, debug, write_combined_file,
            maxWorkgroupSize, inv_memory_density, N_value, openclDevice)

    def run(self, bufStructs, func, pwdIter, salt=b"",
            paddedLenFunc=None, rtnPwds=None):
        # PaddedLenFunc is just for checking: lower bound with original length
        # if not supplied
        wordType = self.wordType
        wordSize = self.wordSize
        ctx = self.ctx
        queue = self.queue
        hashBlockSize_bits = bufStructs.hashBlockSize_bits
        if not paddedLenFunc:
            paddedLenFunc = lambda x, bs: x

        inBufSize_bytes = bufStructs.inBufferSize_bytes
        outBufSize_bytes = bufStructs.outBufferSize_bytes
        outBufferSize = bufStructs.outBufferSize
        saltBufferSize_bytes = bufStructs.saltBufferSize_bytes

        # Main loop is taking chunks of at most the workgroup size
        while True:
            pwArray = bytearray()

            # For each password in our chunk, process it into pwArray, with
            # length first. Notice that this lines up with the struct declared 
            # in the .cl file.
            chunkSize = self.workgroupsize
            for i in range(self.workgroupsize):
                try:
                    pw = pwdIter.__next__()
                    # Since we take a iterator, we feed the passwords back if requested
                    if rtnPwds is not None:
                        rtnPwds.append(pw)
                except StopIteration:
                    # Correct the chunk size and break
                    chunkSize = i
                    break

                pwLen = len(pw)
                # Now passing hash block size as a parameter.. could be None?
                assert paddedLenFunc(pwLen, hashBlockSize_bits // 8) <= inBufSize_bytes, \
                    "password #" + str(i) + ", '" + pw.decode() + "' (length " + str(
                        pwLen) + ") exceeds the input buffer (length " + str(inBufSize_bytes) + ") when padded"

                # Add the length to our pwArray, then pad with 0s to struct size
                # prev code was np.array([pwLen], dtype=np.uint32), this ultimately is equivalent
                pwArray.extend(pwLen.to_bytes(wordSize, 'little')+pw+(b"\x00"* (inBufSize_bytes - pwLen)))

            # print("========= pwArray (bytearray) ============")
            # print(pwArray)

            if chunkSize == 0:
                break
            # print("Chunksize = {}".format(chunkSize))

            # Convert the pwArray into a numpy array, just the once.
            # Declare the numpy array for the digest output
            pwArray = np.frombuffer(pwArray, dtype=wordType)
            result = np.zeros(outBufferSize * chunkSize, dtype=wordType)

            # Allocate memory for variables on the device
            pass_g = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=pwArray)
            result_g = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, result.nbytes)

            # print("========== pwArray (wordType) ============")
            # print(pwArray)

            # print("=========== Initial buffers ==============")
            # print(" pass_g.nbytes = {}".format(pwArray.nbytes))
            # print(" result_g.nbytes = {}".format(result.nbytes))

            # Call Kernel. Automatically takes care of block/grid distribution
            pwdim = (chunkSize,)

            # Main function callback : could adapt to pass further data
            func(self, pwdim, pass_g, None, result_g)

            # Read the results back into our array of int32s, then hexlify
            # Some inefficiency here, unavoidable using hexlify
            cl.enqueue_copy(queue, result, result_g)

            # Chop up into the individual hash digests, then trim to necessary hash length.

            # Yield this block of results
            yield [bytes(result[i:i + outBufSize_bytes // wordSize])
                   for i in range(0, len(result), outBufSize_bytes // wordSize)]

        # No main return
        return None


class zimcoin_algos(opencl.opencl_algos):
    """
    Provide custom functions for zimcoin tests and mining.
    """
    def __init__(self, platform, debug, write_combined_file, inv_memory_density=1, openclDevice = 0):
        super().__init__(platform, debug, write_combined_file, inv_memory_density, openclDevice)
        self.opencl_ctx = zimcoin_interface(platform, debug, write_combined_file, openclDevice = openclDevice)

    def cl_init(self, option="zimcoin.cl", max_in_bytes=128, max_salt_bytes=32, 
            dklen=0, max_ct_bytes=0):
        """
        Initialize the hash function that generates a single hash.
        """
        bufStructs = buffer_structs()
        bufStructs.specifySHA2(256, max_in_bytes, max_salt_bytes, dklen, max_ct_bytes)
        assert bufStructs.wordSize == 4  # set when you specify sha256

        prg = self.opencl_ctx.compile(
            bufferStructsObj=bufStructs,
            library_file='sha256.cl',
            footer_file=option)
        
        return [prg, bufStructs]

    def cl_hash_single(self, ctx, passwordlist):
        # self.cl_sha256_init()
        prg = ctx[0]
        bufStructs = ctx[1]

        def func(s, pwdim, pass_g, salt_g, result_g):
            prg.single_hash(s.queue, pwdim, None, pass_g, result_g)
            #prg.hash_main(s.queue, pwdim, None, pass_g, result_g)

        return concat(self.opencl_ctx.run(
            bufStructs, func, iter(passwordlist), b"", mdpad_64_func))
