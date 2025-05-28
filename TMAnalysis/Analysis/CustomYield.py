#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   CustomYield.py
#
#   PURPOSE: Get the yield stress for a custom strain offset.
#
#   INPUTS:
#       strain         strain vector
#       stress         stress vector
#       modulus        elastic modulus
#       offset         offset strain value
#   OUTPUTS:
#       yield_stress   yield stress at offset strain value
#       yield_strain   corresponding strain to yeild stress
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CustomYield(strain, stress, modulus, offset):
    # Import modules
    import numpy as np

    # Set Yield Line End Points
    p0_x = offset
    p0_y = 0
    p1_x = 1.2*max(stress)/modulus+offset 
    p1_y = 1.2*max(stress)

    # Initialize Yield stress and strain
    yield_stress = None
    yield_strain = None

    # Find Intersection Points if they exist
    i = 0
    while yield_strain == None:
        # LeMothe's Algorithm for Line Intersection
        p2_x = strain[i]
        p2_y = stress[i]
        p3_x = strain[i+1] 
        p3_y = stress[i+1]

        s1_x = p1_x - p0_x     
        s1_y = p1_y - p0_y
        s2_x = p3_x - p2_x     
        s2_y = p3_y - p2_y

        s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y);
        t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y);

        if s >= 0 and s <= 1 and t >= 0 and t <= 1:
            yield_strain = p0_x + (t*s1_x)
            yield_stress = p0_y + (t*s1_y)

        if i < len(strain)-2:
            i = i+1
        else:
            break

        if yield_stress != None:
            idx = np.where(abs(stress-yield_stress) == min(abs(stress-yield_stress)))[0][0]
            yield_stress = stress[idx]
            yield_strain = strain[idx]

    return yield_stress, yield_strain