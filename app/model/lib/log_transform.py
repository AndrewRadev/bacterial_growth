import numpy as np


def apply_log_transform(df):
    # Find an non-negative threshold to use as a clamping lower limit
    min_value = np.min(df[df['value'] > 0]['value'])
    lower_threshold = min_value / 10.0

    with np.errstate(divide='ignore', invalid='ignore'):
        df['log_value'] = np.log(df['value'])

    if 'std' in df:
        # Transform std values by summing them and transforming the results.
        # The std values are absolute lengths of the error bars in either
        # direction.
        with np.errstate(divide='ignore', invalid='ignore'):
            upper_point = df['value'] + df['std']
            df['log_std_upper'] = np.log(upper_point) - df['log_value']

            # Lower point is clamped to one order of magnitude (1/10) below the
            # lowest positive value - std in the data frame. If we don't do
            # this, we get negative inifinities for lower margins.
            lower_point = np.clip(df['value'] - df['std'], min=lower_threshold)
            df['log_std_lower'] = np.abs(df['log_value'] - np.log(lower_point))

    return df
