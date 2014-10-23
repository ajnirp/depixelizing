cython depix.pyx
gcc -O3 -c -fPIC depix.c -L/usr/local/lib/python2.7/ -lpython2.7 -I/usr/include/python2.7/
gcc -shared depix.o -o depix.so