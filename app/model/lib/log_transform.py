import numpy as np


def apply_log_transform(df):
    with np.errstate(divide='ignore', invalid='ignore'):
        df['log_value'] = np.log(df['value'])

    if 'std' in df:
        # Transform std values by summing them and transforming the results:
        with np.errstate(divide='ignore', invalid='ignore'):
            df['log_std_upper'] = np.log(df['value'] + df['std']) - df['log_value']
            df['log_std_lower'] = np.abs(df['log_value'] - np.log(np.clip(df['value'] - df['std'], min=1)))

    # If the results produced infinities, remove them:
    df = df.replace([np.inf, -np.inf], np.nan)

    return df
