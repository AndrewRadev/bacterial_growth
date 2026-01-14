## Types of techniques

To extract actionable insights from raw growth data, we need to apply some kind of systematic approach that summarizes observations into comparable metrics. Depending on our use case, we may choose from a variety of different methods, each with their benefits and drawbacks.

**Mechanistic** methods attempt to simulate the process of growth under specific assumptions, which take the form of a mathematical model. **Phenomenological** methods only describe the observed patterns of growth and allow us to extract properties of the data. They may fit the growth measurements to a model, but they could also be "model-free", or "nonparametric". In that case, the data is examined through some algorithm that finds the desired property without fitting the growth curve to a parameterized function.

μGrowthDB provides several methods to fit growth data using the [growthrates](https://github.com/tpetzoldt/growthrates) R package.

<h2 id="easy_linear">"Easy linear" method</h2>

This algorithm consists of iterating through windows of 5 sequential time points and performing a linear regression on the natural logarithm of the cell abundances at those points. The maximum discovered slope is used to determine the final growth rate. While the method uses five-point windows by default, the growthrates package has flexible input parametrization, allowing the user to vary this number.

More information: "[Growth Rates Made Easy](https://doi.org/10.1093/molbev/mst187)"

<h2 id="logistic">Logistic model</h2>

A simple way to describe exponential growth is by using the first-order ordinary differential equation (ODE) shown here:

\begin{align}
\frac{dy}{dx} & = \mu y\\\\
y(x)          & = y_0 e^{\mu (x - x_0)}
\end{align}

In formula (1), \\(x\\) denotes time, \\(y\\) denotes the number of cells at that time, and \\(\mu\\) is a specific growth rate constant. At every time point, the population is increased by \\(\mu\\) times the current population. The analytical solution (2) calculates the population at time \\(x\\) based on the starting time \\(x_0\\) and initial population \\(y_0\\).

In practice, exponential growth does not continue indefinitely. The mechanistic logistic model adds a constant \\(K\\) to this equation that represents the carrying capacity of the environment:

\begin{align}
\frac{dy}{dx} & = \mu_{max} y (1 - \frac{y}{K})\\\\
y(x)          & = \frac{K}{1 + (\frac{K - y_0}{y_0})e^{-\mu_{max} x}}
\end{align}

When \\(y\\) is fairly low, the second term in the brackets of the second equation is close to zero, so the population experiences exponential growth. As \\(y\\) approaches the carrying capacity, growth slows down to zero. The constant \\(μ\\) has been replaced with the maximum specific growth rate constant \\(\mu_{max}\\) to distinguish between the observed growth rate at any particular time point and the greatest potential growth rate.

<h2 id="baranyi_roberts">Baranyi-Roberts model</h2>

The goal of this model is to fit and parameterize the lag phase of growth as well as the exponential and stationary phases. Baranyi and Roberts define a time-dependent variable \\(q(t)\\) that represents the physiological state of the cell and derive an "adjustment function" \\(\alpha(t)\\) to describe what portion of the potential maximum growth rate is usable by the cell at time \\(t\\):

\begin{align}
  \alpha(t) = \frac{q(t)}{1 + q(t)}
\end{align}

Equation (6) shows a transformation of this \\(\alpha\\) function that is practically useful for computational purposes. The value of this function at time 0, \\(h_0 = h(0)\\), is the product of the maximum specific growth rate and the lag time. For a particular growth curve, it is a constant that can be fitted.

\begin{align}
  h(t) & = ln(1 + \frac{1}{q(t)}) = -ln(\alpha(t))
\end{align}

The authors find this definition useful, because it allows the separation of **intrinsic** parameters like \\(\mu_{max}\\) that are only dependent on the microorganism in a specific environment, and **controlling** parameters like \\(h_0\\) that are only dependent on the experimenter (e.g. the condition of the initial inoculum in the experiment). They stress that, under their model, the adjustment function may be influenced by changes in the environment like temperature, so \\(h_0\\) can be used as a parameter only under fixed conditions.

The model also includes a limiting function depending on a maximum cell density parameter, similar to the carrying capacity of the logistic model. The R package growthrates uses the following solution of the Baranyi-Roberts differential equation for fitting the data:

\begin{align}
  A = x + \frac{1}{\mu_{max}} ln(e^{-\mu_{max} x} + e^{-h_0} - e^{-\mu_{max} x - h_0})\\\\
  ln(y) = ln(y_0) + \mu_{max}A - ln(1 + \frac{e^{\mu_{max}A} - 1}{e^{ln(K) - ln(y_0)}})
\end{align}

Here, time is denoted by \\(x\\) and cell abundances by \\(y\\).

More information:

- "[A non-autonomous differential equation to model bacterial growth](https://doi.org/10.1006/fmic.1993.1005)"
- "[A dynamic approach to predicting bacterial growth in food](https://doi.org/10.1016/0168-1605(94)90157-0)"
- "[Mathematics of predictive food microbiology](https://doi.org/10.1016/0168-1605(94)00121-L)"
