#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Linear_Analysis.py
#
#   PURPOSE: Identify the linear portion of a stress-strain curvea and extract modulus, proportional
#            limit and strain at proportional limit
#
#   INPUTS:
#     strain      nx1 array of strain data points
#     stress      nx1 array of stress data points
#     diamstrain  nx1 array of strain in the transverse direction
#
#   OUTPUTS:
#     mod                      modulus of elasticity
#     prop                     proportional limit stress
#     prop_e                   proportional limit strain
#     PR                       Poisson's Ratio
#     [idx_Start, lin_idx]     indicies of the start and end of the linear region
#     mod_info                 linear fit information (for plotting only)
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def Linear_Analysis(strain, stress, diamstrain):
    # Import Modules
    import numpy as np
    import scipy.stats

    # Find the index of the max load
    idx_max = np.where(stress == max(stress))[0][0]

    # Set Start Index at 5% of max load -- offset to prevent compliance issues
    idx_start = int(0.05*idx_max)

    # Set End Index initially to twice the start index    
    idx_end = 2*idx_start

    # Look between start and max load for change in linearity
    lin_end = idx_max
    while idx_end < idx_max:
        # Calculate the linear fit
        mod_info = scipy.stats.linregress(strain[idx_start:idx_end], stress[idx_start:idx_end])
        
        # Check fit against linearity constraint
        if mod_info.rvalue < 0.99975:
            lin_end = idx_end
            break

        # Update the end index
        idx_end = idx_end + 1

    # Get Parameters
    # -- Elastic Modulus equal to fit slope
    mod = mod_info.slope

    # -- Only set proportional limit if material non-linearity is identified
    if lin_end < idx_max:
        prop = stress[lin_end]
        prop_e = strain[lin_end]
    else:
        prop = None
        prop_e = None

    # Calculate Poisson's Ratio (if applicable)
    PR = None
    if len(diamstrain) != 0:
        PR_fit = scipy.stats.linregress(strain[idx_start:lin_end], -diamstrain[idx_start:lin_end])
        if PR_fit.slope > 0 and PR_fit.slope < 0.5:
            PR= PR_fit.slope

    return mod, prop, prop_e, PR, [idx_start, lin_end], mod_info