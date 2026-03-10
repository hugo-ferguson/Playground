# Terminal Velocity Calculator
# This program calculates the terminal velocity of a character in air, 
# given their mass and dimensions.

import constants
import math

def calc_surface_area(height: float, width: float) -> float:
    # The ratio of the frontal surface area of a body to 
    # a perfectly rectangular surface area (how square a body is)
    return height * width * constants.BODY_RECT_FACTOR

def feet_to_m(value: float) -> float:
    # Convert feet to metres
    return value * constants.FEET_TO_M

def m_to_feet(value: float) -> float:
    # Convert metres to feet
    return value / constants.FEET_TO_M

def calc_terminal_v(mass: float, surface_area: float):
    # Calculate the terminal velocity of character in air (in m s^-1)
    return math.sqrt((2 * mass * constants.ACCEL_G) / \
        (constants.DENSITY_AIR * surface_area * constants.COEFF_DRAG_BODY))

def main():
    # Get the character dimensions (and store in m)
    body_height = feet_to_m(float(input('Enter Height of Character (in feet): ')))
    body_width = feet_to_m(float(input('Enter Width of Character (in feet): ')))
    body_mass = float(input('Enter Mass of Character (in kg): '))

    # Calculate projected surface area (in m^2)
    body_surface_area = calc_surface_area(body_height, body_width)

    # Calculate terminal velocity (in m s^1)
    terminal_v = calc_terminal_v(body_mass, body_surface_area)

    # Output terminal velocity (in ft s^1)
    print(f'Terminal Velocity (in ft/s): {m_to_feet(terminal_v): 0.2f}')

if __name__ == "__main__":
    main()