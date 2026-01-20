library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv         = 'input.csv'
coefficients_json = 'coefficients.json'
fit_json          = 'fit.json'

data <- read.table(input_csv, header=T, sep=',')

## Initial parameter estimation from easy linear fit
model_fit <- fit_easylinear(data$time, data$value, h=min(5, length(data$time) - 1))
el_coefficients = coef(model_fit)

y0_est    = el_coefficients['y0']
mumax_est = el_coefficients['mumax']
lag_est   = el_coefficients['lag']
h0_est    = mumax_est * lag_est

max_value = max(data$value)

p <- c(y0    = max(y0_est,    10),
       mumax = max(mumax_est, 1e-5),
       K     = max(max_value, 1e+3),
       h0    = max(h0_est,    1e-4))

print("Initial estimation:")
print(p)

lower <- c(y0    = 1,
           mumax = 1e-6,
           K     = 1e+2,
           h0    = 1e-9)

# Fitting methods:
# "Marq", "Port", "Newton", "Nelder-Mead", "BFGS", "CG", "L-BFGS-B", "SANN", "Pseudo", "bobyqa"

model_fit <- fit_growthmodel(FUN       = grow_baranyi,
                             method    = 'BFGS',
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
