#include <stdio.h>
#include "SDL.h"

// best not to ask about why this is necessary
#undef main

int main() {
    SDL_Init(SDL_INIT_JOYSTICK);
    SDL_Joystick* stick = SDL_JoystickOpen(0);
    while (1) {
        SDL_JoystickUpdate();
        printf("[%d,%d]\n",
               SDL_JoystickGetAxis(stick, 0),
               SDL_JoystickGetAxis(stick, 1));
    }
}

