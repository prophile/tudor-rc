#include <stdio.h>
#include "SDL.h"

// best not to ask about why this is necessary
#undef main

int main() {
    SDL_Init(SDL_INIT_JOYSTICK);
    SDL_Joystick* stick = SDL_JoystickOpen(0);
    while (1) {
        SDL_JoystickUpdate();
        printf("[%d,%d,%s]\n",
               SDL_JoystickGetAxis(stick, 3),
               SDL_JoystickGetAxis(stick, 1),
               SDL_JoystickGetButton(stick, 0) ? "true" : "false");
        fflush(stdout);
        SDL_Delay(100);
    }
}

