Page('.sandbox-page', function($page) {
  $page.find('.js-upload-container-left').customFileInput();
  $page.find('.js-upload-container-right').customFileInput();

  let $leftFileInput  = $('.js-upload-container-left input[type=file]');
  let $rightFileInput = $('.js-upload-container-right input[type=file]');

  let $submitButton = $page.find('input[type=submit]');

  $page.on('change', 'input[type=file]', updateSubmitState)
  $page.on('reset', 'form', function() {
    setTimeout(updateSubmitState, 1);
  });

  updateLogView();
  $page.on('change', '.js-log-left,.js-log-right', updateLogView);

  function updateSubmitState() {
    if ($leftFileInput[0].files.length + $rightFileInput[0].files.length > 0) {
      $submitButton.prop('disabled', false);
    } else {
      $submitButton.prop('disabled', true);
    }
  }

  function updateLogView() {
    let updates = {}

    let $logLeft = $page.find('.js-log-left');
    if (!$logLeft.is(':disabled')) {
      if ($logLeft.is(':checked')) {
        updates['yaxis.type'] = 'log';
      } else {
        updates['yaxis.type'] = 'linear';
      }
    }

    let $logRight = $page.find('.js-log-right');
    if (!$logRight.is(':disabled')) {
      if ($logRight.is(':checked')) {
        updates['yaxis2.type'] = 'log';
      } else {
        updates['yaxis2.type'] = 'linear';
      }
    }

    if (Object.keys(updates).length > 0) {
      $page.find('.js-plotly-plot').each(function() {
        Plotly.relayout(this, updates);
      });
    }
  }
})
