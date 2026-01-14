## Fitting models

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/modeling/fitting-models.png"
        title="Modeling interface" />
</div>

The application provides an interface to fit a limited number of growth models, supported by the R package [growthrates](https://github.com/tpetzoldt/growthrates). You can find descriptions of these models and links to further information in the "[Modeling Techniques](/help/modeling-techniques)" help topic.

After you upload your study, you will see a "Fit models" button in its navigation interface. That page is very similar to the "Visualize" page, but allows visualizing only one data trace at a time. You can filter by experiment and measurement technique to find a specific growth curve to fit. Select a "Modeling type" from the dropdown and then click "Calculate" to try to generate a fit.

The calculation process runs in the background, so you can refresh the page or navigate away if it takes too long. You can also go through several data traces and trigger calculations without waiting for the previous one to finish. Once it's done, you should see the model trace shown on the chart with the model's parameters listed below. You can click "Publish" to make this model visible to visitors to the site, but your fits are hidden by default. You're free to experiment with different models and parameterizations before determining which one produces the best fit to the data.

The calculation may fail with an error message if the fitting process fails to converge. In that case, consider picking a different model or parameters. For instance, the chart on the right is fitted with Baranyi-Roberts on the first 16 hours of data, since that's where we can see the growth curve reach its peak, and this particular model is not intended to fit the death phase of microbial growth.

## Uploading custom model data

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/modeling/custom-models.png"
        title="Modeling interface" />
</div>

Instead of trying to fit models through μGrowthDB, you may wish to perform this process yourself. This can give you the most flexibility and allow you to use a modeling approach beyond what the site offers. In that case, you can select "Custom model" from the modeling dropdown and describe the details of your modeling approach. Ideally, you should provide a link to wherever your modeling software is located or a publication that describes it. You can also select what common coefficients (maximum growth rate, lag time, carrying capacity...) your model uses. This can be used by researchers to extract quantifiable metrics from your models.

Once the specifics of the model are described, you can upload CSV files for model predictions corresponding to specific data traces. Ideally, this file would include around 100-200 data points that visualize the model curve. These will be stored in our database, along with any parameters and measures of fit that you fill in the form.

Each model upload needs to be attached to a specific measurement curve, but this does not imply that you need to use only this data trace for fitting. For instance, a model might use both growth curves and metabolite measurements to approximate a particular species' growth behaviour. The resulting predictions may then be uploaded to one of the measured data traces under the specific conditions that the model assumes.

## Model visualization

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/modeling/visualize-models-1.png"
        title="Modeling interface" />
</div>

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/modeling/visualize-models-2.png"
        title="Modeling interface" />
</div>

Once models are published, their techniques will be shown in the study page under "Modeling techniques". The info buttons will lead visitors to more information about the modeling process. If you've added a custom model, the buttons will link to the information URL that you provided.

The button "Download model parameters" links to a CSV with all published models and their recorded coefficients and quality of fit measurements. If you're the owner of the study or have permission to manage it, you'll get data on the non-published ones as well. This button is also available on the "Fit models" page.

In the "Visualize" section, researchers can pick published model visualizations attached to their corresponding measurement traces. These curves can also be added to the "Compare" view and compared between studies.

<div class="clear"></div>
