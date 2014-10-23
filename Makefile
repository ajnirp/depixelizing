main.c: main.py
	cython main.py

main.o: main.c
	gcc -O3 -c -fPIC main.c -L/usr/local/lib/python2.7/ -lpython2.7 -I/usr/include/python2.7/

main.so: main.o
	gcc -shared main.o -o main.so

all:
	cython main.py
	gcc -O3 -c -fPIC main.c -L/usr/local/lib/python2.7/ -lpython2.7 -I/usr/include/python2.7/
	gcc -shared main.o -o main.so
	python so.py

clean:
	rm -f *.o *.so *.c