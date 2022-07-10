__kernel void single_hash(__global const inbuf * inbuffer, __global outbuf * outbuffer)
{
    // test word "hell"
    uchar w[4] = {104, 101, 108, 115};

    // manually create the input for now assuming len is 4
    unsigned int input_buffer[32];

//     input_buffer[0] = (w[3] << 24) | (w[2] << 16) | ( w[1] << 8 ) | (w[0]);
//     // for (int i = 1; i < 32; i++) {
//     //     input_buffer[i] = 0;
//     // } 

//     //hash_global(&input_buffer, 4 outbuffer[0].buffer);
}