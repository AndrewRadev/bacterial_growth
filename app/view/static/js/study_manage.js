Page('.study-manage-page', function($page) {
  let studyId = $page.data('studyId');
  let $form   = $page.find('.js-modeling-form');

  updateFormVisibility($form);
  let $activeRadio = $('.js-technique-row:visible input[type=radio]:checked');
  if ($activeRadio.length > 0) {
    updateChart($activeRadio.first());
  }

  $page.find('.js-experiment-container').each(function(e) {
    let $container = $(this);

    if ($container.find('input[type=checkbox]:checked').length > 0) {
      $container.removeClass('hidden');
      return;
    }
  });

  $page.on('change', 'form.js-modeling-form', function(e) {
    let $form = $(e.currentTarget);
    updateFormVisibility($form);

    let $activeRadio = $('.js-technique-row:visible input[type=radio]:checked');
    if ($activeRadio.length > 0) {
      updateChart($activeRadio.first());
    }
  });

  $page.on('click', '.js-select-all', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox].js-measurement-toggle:visible').prop('checked', true);

    updateFormVisibility($form)
  });

  $page.on('click', '.js-clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox]').prop('checked', false);

    updateFormVisibility($form)
  });

  $page.on('submit', '.js-modeling-form', function(e) {
    e.preventDefault();
    let $form = $(e.currentTarget);

    let modelingType = $form.find('select[name=modelingType]').val();
    let $activeRow   = $('.js-technique-row.highlight:visible');

    $.ajax({
      url: $form.attr('action'),
      dataType: 'json',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        let modelingRequestId = response.modelingRequestId;
        let $formResult       = $page.find('.js-calculation-result');

        if ($activeRow.find('[data-modeling-result-id]').length == 0) {
          $activeRow.append(`<div data-modeling-result-id="${modelingResultId}">⏳</div>`);
        }

        function check() {
          $.ajax({
            url: `/study/${studyId}/modeling/check.json`,
            dataType: 'json',
            success: function(response) {
              let allReady = true;

              for (const [resultId, resultState] of Object.entries(response)) {
                let $indicator = $page.find(`[data-modeling-result-id=${resultId}]`);

                if (!resultState.ready) {
                  allReady = false;
                  $indicator.text('⏳');
                } else if (!resultState.successful) {
                  $indicator.text('❌');
                } else {
                  $indicator.text('✅');
                }
              }

              let $activeRadio = $activeRow.find('input[type=radio]:checked');
              if ($activeRadio.length > 0) {
                updateChart($activeRadio.first());
              }

              if (!allReady) {
                $formResult.html('⏳ Calculating...');
                setTimeout(check, 1000);
              } else {
                $formResult.html("Calculations finished. Submit the form to perform another calculation");
              }
            }
          });
        }

        check();
      }
    })
  });

  function updateMeasurementSubjects($form) {
    let $techniqueSelect = $form.find('.js-technique-type');
    let techniqueId = $techniqueSelect.val();

    $form.find('[data-technique-id]').addClass('hidden')
    $form.find(`[data-technique-id=${techniqueId}]`).removeClass('hidden')
  }

  // TODO: duplicates study_visualize.js, except for the form submission
  function updateFormVisibility($form) {
    let selectedExperimentId = $form.find('select[name="experimentId"]:visible').val();

    $form.find('.js-experiment-container').addClass('hidden');
    $form.find('.js-technique-row').addClass('hidden');

    let $experiment = $form.find(`.js-experiment-container[data-experiment-id="${selectedExperimentId}"]`);
    $experiment.removeClass('hidden');

    let selectedTechniqueId = $form.
      find('select[name="techniqueId"]').val();
    let selectedTechniqueSubjectType = $form.
      find('select[name="techniqueId"] option:selected').data('subjectType');

    $experiment.
      find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"]`).
      removeClass('hidden');

    let modelingType = $form.find('select[name=modelingType]').val();
    $form.find('[data-modeling-type]').addClass('hidden');
    $form.find(`[data-modeling-type="${modelingType}"]`).removeClass('hidden');

    $form.find('[data-modeling-input]').addClass('hidden');
    $form.find(`[data-modeling-input-${modelingType}]`).removeClass('hidden');
  }

  function updateChart($radio) {
    let $form = $radio.parents('form');

    let $chart       = $form.find('.js-chart');
    let modelingType = $form.find('select[name=modelingType]').val();
    let logTransform = $form.find('input[name=logTransform]').prop('checked');

    $page.find('.js-technique-row').removeClass('highlight');
    $radio.parents('.js-technique-row').addClass('highlight');

    let measurementContextId = $radio.val().replaceAll('measurementContext|', '');

    $.ajax({
      url: `/study/${studyId}/modeling/${measurementContextId}/chart`,
      dataType: 'html',
      data: {
        'modelingType': modelingType,
        'logTransform': logTransform,
        'width':        $chart.width(),
        'height':       $chart.height(),
      },
      success: function(response) {
        $chart.html(response)
        initTooltips();
      },
    });
  }
});
