MODEL_NAMES = {
    'easy_linear':     '"Easy linear" method',
    'logistic':        'Logistic model',
    'baranyi_roberts': 'Baranyi-Roberts model',
}
"The human-readable names of the supported models/methods"

SHORT_MODEL_NAMES = {
    'easy_linear':     'EL',
    'logistic':        'Log.',
    'baranyi_roberts': 'B.-R.',
}
"Shortened model names to show in charts"

MODEL_DESCRIPTIONS = {
    'easy_linear':     'A phenomenological method that estimates growth rate based on a regression line between observed points.',
    'logistic':        'A model that describes exponential growth limited by a carrying capacity.',
    'baranyi_roberts': 'A mechanistic model that aims to quantify the lag phase.',
}
"One-sentence descriptions of the supported models/methods"

COMMON_MODEL_PARAMETERS = {
    "mumax": {
        "name_html": "μ<sub>max</sub>",
        "description_html": "Maximum growth rate (in h<sup>-1</sup>)"
    },
    "lag": {
        "name_html": "lag",
        "description_html": "Time duration of the lag phase (in hours)"
    },
    "y0": {
        "name_html": "y<sub>0</sub>",
        "description_html": "Initial value of abundance"
    },
    "K": {
        "name_html": "K",
        "description_html": "Carrying capacity (maximum abundance)"
    },
}
"Names and descriptions for common model parameters (growth rate, lag time, etc)"

ALL_MODEL_PARAMETERS = {
    **COMMON_MODEL_PARAMETERS,
    "y0_lm": {
        "name_html": "y<sub>0</sub>_lm",
        "description_html": "y<sub>0</sub> calculated as the intersection of the fit with the abscissa, the initial abundance if there was no lag"
    },
    "h0": {
        "name_html": "h<sub>0</sub>",
        "description_html": "parameter specifying the initial physiological state of organisms (e.g. cells) and in consequence the lag phase (h<sub>0</sub> = max growth rate &times; lag phase)"
    },
}
"Names and descriptions for all model parameters used by models we know of"
