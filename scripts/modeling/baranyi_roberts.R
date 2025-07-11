library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv         = 'input.csv'
coefficients_json = 'coefficients.json'
fit_json          = 'fit.json'

data <- read.table(input_csv, header=T, sep=',')

## Initial parameter estimation from spline fit
spline_fit <- fit_spline(data$time, data$value)
summary(spline_fit)
spline_coefficients <- coef(spline_fit)

y0_est    = spline_coefficients['y0']
mumax_est = spline_coefficients['mumax']
names(y0_est)    <- NULL
names(mumax_est) <- NULL

# TODO: estimate lag time by intercepting max growth with x-axis
# h0_est = mumax_est * lag_time
# h0_est = mumax_est * 5.52495319837189
h0_est = 0.05

max_value = max(data$value)

p <- c(y0    = max(y0_est, 1e-9),
       mumax = max(mumax_est, 1e-9),
       K     = max(max_value, 1e-9),
       h0    = max(h0_est, 1e-9))

lower <- c(y0    = 1e-9,
           mumax = 1e-9,
           K     = 1e-9,
           h0    = 1e-9)

# Fitting methods:
# “Marq”, “Port”, “Newton”, “Nelder-Mead”, “BFGS”, “CG”, “L-BFGS-B”, “SANN”, “Pseudo”, “bobyqa”

model_fit <- fit_growthmodel(FUN       = grow_baranyi,
                             method    = 'CG',
                             transform = 'log',
                             time      = data$time,
                             y         = data$value,
                             p         = p,
                             lower     = lower)

print("## SUMMARY START")
summary(model_fit)
print("## SUMMARY END")

coefficients = coef(model_fit)

f <- file(coefficients_json)
writeLines(toJSON(as.data.frame(coefficients), auto_unbox=T), f)
close(f)

f <- file(fit_json)
fit <- data.frame(r2=rsquared(model_fit), rss=deviance(model_fit))
writeLines(toJSON(fit, auto_unbox=T), f)
close(f)
