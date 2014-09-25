joystick: joystick.c
	clang -L/usr/local/lib -I/usr/local/include/SDL2 -lSDL2 -o $@ $<

clean:
	rm -f joystick

.PHONY: clean

