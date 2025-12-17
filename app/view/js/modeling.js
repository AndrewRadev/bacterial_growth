Page('.study-modeling-page', function($page) {
  let studyId = $page.data('studyId');
  let $form   = $page.find('.js-modeling-form');

  updateFormVisibility($form);
  let $activeRadio = $('.js-technique-row:visible input[type=radio]:checked');

  updateCustomModelVisibility($form, $activeRadio);
  if ($activeRadio.length > 0) {
    updateChart($activeRadio.first());
    updateSelectedContext($activeRadio.first());
  }

  let $pendingIndicators = $page.find('[data-modeling-state=pending]');
  if ($pendingIndicators.length > 0) {
    checkForUpdates();
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
    let $activeRadio = $page.find('.js-technique-row:visible input[type=radio]:checked');

    updateCustomModelVisibility($form, $activeRadio);
    if ($activeRadio.length > 0) {
      updateChart($activeRadio.first());
      updateSelectedContext($activeRadio.first());
    }
  });

  $page.on('submit', '.js-modeling-form', function(e) {
    e.preventDefault();
    let $form = $(e.currentTarget);

    let $activeRow = $('.js-technique-row.highlight:visible');

    $.ajax({
      url: $form.attr('action'),
      dataType: 'json',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        let modelingResultId = response.modelingResultId;

        if ($activeRow.find('[data-modeling-result-id]').length == 0) {
          $activeRow.append(`<div data-modeling-result-id="${modelingResultId}">⏳</div>`);
        }

        checkForUpdates();
      }
    })
  });

  $page.on('click', '.js-toggle-published', function(e) {
    e.preventDefault();

    let $button = $(e.currentTarget);
    let url     = $button.data('url');

    $form.find('input').prop('disabled', true);

    $.ajax({
      url: url,
      dataType: 'json',
      method: 'POST',
      success: function(response) {
        $form.find('input').prop('disabled', false);
        let $activeRadio = $('.js-technique-row:visible input[type=radio]:checked');
        updateChart($activeRadio.first());
      },
      error: function() {
        $form.find('input').prop('disabled', false);
      }
    })
  });

  $page.on('click', '.js-edit-model', function(e) {
    let $parentContainer = $(this).parents('.js-preview');
    let $form = $parentContainer.next('form[data-custom-model-id]');

    $parentContainer.addClass('hidden');
    $form.removeClass('hidden');
  });

  $page.on('click', '.js-cancel-edit-model', function(e) {
    let $form = $(this).parents('form[data-custom-model-id]');
    let $preview = $form.prev('.js-preview');

    $form.addClass('hidden');
    $preview.removeClass('hidden');
  });

  $page.on('click', '.js-delete-model', function(e) {
    let $button = $(this);

    if (confirm($button.data('confirm'))) {
      $.ajax({
        url: $button.data('url'),
        method: 'POST',
        success: function() {
          window.location.reload();
        }
      });
    }
  });

  function updateMeasurementSubjects($form) {
    let $techniqueSelect = $form.find('.js-technique-type');
    let techniqueId = $techniqueSelect.val();

    $form.find('[data-technique-id]').addClass('hidden')
    $form.find(`[data-technique-id=${techniqueId}]`).removeClass('hidden')
  }

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
  }

  function updateCustomModelVisibility($form, $activeRadio) {
    let $modelingType = $form.find('select[name=modelingType]');
    let modelingType = $modelingType.val();
    let customModelId = $modelingType.find('option:selected').data('customModelId');

    $form.find('[data-modeling-type]').addClass('hidden');
    $form.find(`[data-modeling-type="${modelingType}"]`).removeClass('hidden');

    $form.find('[data-modeling-input]').addClass('hidden');
    $form.find(`[data-modeling-input-${modelingType}]`).removeClass('hidden');

    if (modelingType.startsWith('custom_')) {
      $form.find('.js-calculation-status').hide();

      if (modelingType == 'custom_new') {
        $page.find('.js-custom-model-form').removeClass('hidden');
        $page.find(`.js-custom-model-form form`).addClass('hidden');
        $page.find(`.js-custom-model-form form[data-custom-model-id=new]`).removeClass('hidden');

        $page.find('.js-custom-upload-form').addClass('hidden');
      } else {
        $page.find('.js-custom-model-form').removeClass('hidden');
        $page.find(`.js-custom-model-form form`).addClass('hidden');

        if ($activeRadio.length > 0) {
          $page.find('.js-custom-upload-form').removeClass('hidden');
          $page.find(`.js-custom-upload-form form[data-custom-model-id=${customModelId}]`).removeClass('hidden');
        }
      }
    } else {
      $form.find('.js-calculation-status').show();

      $page.find('.js-custom-model-form').addClass('hidden');
      $page.find(`.js-custom-model-form form`).addClass('hidden');

      $page.find('.js-custom-upload-form').addClass('hidden');
      $page.find(`.js-custom-upload-form form`).addClass('hidden');
    }
  }

  function updateChart($radio) {
    let $form = $radio.parents('form');
    $form.find('input').prop('disabled', true);

    let $chart       = $form.find('.js-chart');
    let modelingType = $form.find('select[name=modelingType]').val();
    let logTransform = $form.find('input[name=logTransform]').prop('checked');
    let isPublished  = $form.find('input[name=isPublished]').prop('checked');

    $page.find('.js-technique-row').removeClass('highlight');
    $radio.parents('.js-technique-row').addClass('highlight');

    let measurementContextId = $radio.val().replaceAll('measurementContext|', '');

    $.ajax({
      url: `/modeling/${studyId}/chart/${measurementContextId}/`,
      dataType: 'html',
      data: {
        'modelingType': modelingType,
        'logTransform': logTransform,
        'isPublished':  isPublished,
      },
      success: function(response) {
        $chart.html(response)
        $form.find('input').prop('disabled', false);
        initTooltips();
      },
      error: function() {
        $form.find('input').prop('disabled', false);
      }
    });
  }

  function updateSelectedContext($radio) {
    let radioValue       = $radio.val();
    let measurementLabel = $radio.data('measurementLabel');
    let unitsLabel       = $radio.data('unitsLabel');
    let contextId        = parseInt(radioValue.replaceAll('measurementContext|', ''), 10);

    $page.find('input[name=selectedMeasurementContextId]').val(contextId);
    $page.find('.js-measurement-label').html(measurementLabel);
    $page.find('.js-units-label').html(unitsLabel);
  }

  function checkForUpdates() {
    $.ajax({
      url: `/modeling/${studyId}/check.json`,
      dataType: 'json',
      success: function(response) {
        let $calculationResult = $page.find('.js-calculation-result');
        let allReady = true;

        for (const [resultId, resultState] of Object.entries(response)) {
          let $indicator = $page.find(`[data-modeling-result-id=${resultId}]`);

          if (resultState == 'ready') {
            $indicator.text('✅');
          } else if (resultState == 'error') {
            $indicator.text('❌');
          } else if (resultState == 'pending') {
            allReady = false;
            $indicator.text('⏳');
          }
        }

        if (allReady) {
          $calculationResult.html("Calculations finished. Submit the form to perform another calculation");

          let $activeRadio = $page.find('.js-technique-row:visible input[type=radio]:checked');
          if ($activeRadio.length > 0) {
            updateChart($activeRadio.first());
          }
        } else {
          $calculationResult.html('⏳ Calculating...');
          setTimeout(checkForUpdates, 1000);
        }
      }
    });
  }
});
