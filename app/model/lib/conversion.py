MEASUREMENT_RATIOS = {
    # (Source,   Target):     source * ratio = target
    ('Cells/μL', 'Cells/mL'): 1_000,
    ('CFUs/μL',  'CFUs/mL'):  1_000,
    ('mM',       'μM'):       1_000,
    ('mM',       'nM'):       1_000_000,
    ('mM',       'pM'):       1_000_000_000,
    ('μM',       'nM'):       1_000,
    ('μM',       'pM'):       1_000_000,
    ('nM',       'pM'):       1_000,
}
"A conversion table for the ratios between pairs of units"

CELL_COUNT_UNITS = ('Cells/mL', 'Cells/μL')
"Units that measure number of cells per volume"

CFU_COUNT_UNITS  = ('CFUs/mL', 'CFUs/μL')
"Units that measure number of CFUs per volume"

METABOLITE_UNITS = ('mM', 'μM', 'nM', 'pM', 'g/L', 'mg/L')
"Units for metabolites, both molar and mass concentration"


def convert_df_units(df, source_units, target_units, metabolite_mass=None):
    """
    Converts the "value" and "std" columns of a dataframe from the source units
    to the target units, if possible.

    Returns the target units on success, or the source units if the requested
    target units are incompatible (e.g. Cells/mL and CFUs/mL).
    """
    new_value = convert_measurement_units(
        df['value'],
        source_units,
        target_units,
        mass=metabolite_mass,
    )

    if new_value is not None:
        df['value'] = new_value
        if 'std' in df:
            df['std'] = convert_measurement_units(
                df['std'],
                source_units,
                target_units,
                mass=metabolite_mass,
            )
        return target_units
    else:
        return source_units


def convert_measurement_units(
    value,
    source_units,
    target_units,
    mass=None,
):
    """
    Convert an individual value (or a numpy array) from the given source unit
    to the given target unit. Returns None if the units are incompatible (e.g.
    Cells/mL and CFUs/mL).

    There is special handling for molar concentrations and mass concentrations
    for metabolites, where the function expects the mass of the metabolite to
    perform the conversion. If the mass is not given in this case, the function
    returns None.
    """
    if source_units == target_units:
        return value

    if source_units in ('g/L', 'mg/L'):
        if mass is None:
            return None
        value /= float(mass)
        if source_units == 'g/L':
            value *= 1000
        source_units = 'mM'

    if target_units in ('g/L', 'mg/L'):
        if mass is None:
            return None
        value *= float(mass)
        if target_units == 'g/L':
            value /= 1_000.0
        target_units = 'mM'

    if source_units == target_units:
        return value

    if (source_units, target_units) in MEASUREMENT_RATIOS:
        ratio = MEASUREMENT_RATIOS[(source_units, target_units)]
        return value * ratio
    elif (target_units, source_units) in MEASUREMENT_RATIOS:
        ratio = MEASUREMENT_RATIOS[(target_units, source_units)]
        return value / ratio
    else:
        return None


def convert_time(time, source, target):
    """
    Converts the given time value from the source units to the target units by
    converting the input to seconds first and then to the given target. The
    minimum resolution supported is "s" for seconds.
    """
    if source == target:
        return time

    # Convert down to seconds:
    if source == 's':
        seconds = time
    elif source == 'm':
        seconds = round(float(time) * 60)
    elif source == 'h':
        seconds = round(float(time) * 3600)
    elif source == 'd':
        seconds = round(float(time) * 86_400)
    else:
        raise ValueError(f"Conversion from {source} to seconds unsupported")

    # Convert up to what was requested
    if target == 's':
        result = seconds
    elif target == 'm':
        result = seconds / 60
    elif target == 'h':
        result = seconds / 3600
    elif target == 'd':
        result = seconds / 86_400
    else:
        raise ValueError(f"Conversion from seconds to {target} unsupported")

    return round(result, 2)
