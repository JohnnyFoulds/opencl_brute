from Library import opencl
from Library.buffer_structs import buffer_structs
from Library.opencl import concat, mdpad_64_func

class zimcoin_interface(opencl.opencl_interface):
    """
    Provide custom functions for zimcoin tests and mining.
    """
    def __init__(self, platform_number, debug=0, write_combined_file=True, inv_memory_density=1):
        super().__init__(platform_number, debug, write_combined_file, inv_memory_density)

class zimcoin_algos(opencl.opencl_algos):
    """
    Provide custom functions for zimcoin tests and mining.
    """
    def __init__(self, platform_number, debug=0, write_combined_file=True, inv_memory_density=1):
        super().__init__(platform_number, debug, write_combined_file, inv_memory_density)

    def cl_hash_init(self, option="zimcoin.cl", max_in_bytes=128, max_salt_bytes=32, 
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

    def cl_hash(self, ctx, passwordlist):
        # self.cl_sha256_init()
        prg = ctx[0]
        bufStructs = ctx[1]

        def func(s, pwdim, pass_g, salt_g, result_g):
            prg.hash_main(s.queue, pwdim, None, pass_g, result_g)

        return concat(self.opencl_ctx.run(
            bufStructs, func, iter(passwordlist), b"", mdpad_64_func))
