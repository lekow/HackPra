PYVERSION=2.7
PYPREFIX=/usr
INCLUDES=-I$(PYPREFIX)/include/python$(PYVERSION)

default: ping clean

ping: ping.o
	@gcc -o $@ $^ -lpython$(PYVERSION)

ping.o: ping.c
	@gcc -c $^ $(INCLUDES)

ping.c: ping.pyx
	@cython3 --embed ping.pyx -2

.PHONY: clean
clean:
	@rm *.c *.o
