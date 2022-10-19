default: compile clean

compile:
	@g++ -c -o hello.o hello.cpp
	@g++ -o hello hello.o
	@g++ -fPIC -c -o sandbox.o sandbox.cpp
	@g++ -shared -o sandbox.so sandbox.o -ldl

.PHONY: clean
clean:
	@rm *.o
