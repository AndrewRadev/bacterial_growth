// TODO: a bunch of things duplicated with study visualization, should refactor
//
Page('.comparison-page', function($page) {
  let $form = $page.find('.js-chart-form');

  updateChart($form).then(function() {
    let checkboxesChanged = false;

    // For each row in the preview form, check if it should be initialized on
    // the left or right:
    $form.find('.js-contexts-list .js-row').each(function() {
      let $chartRow = $(this);

      let contextId = $chartRow.data('contextId');
      let modelId = $chartRow.data('modelId');
      let $formRow;

      if (contextId) {
        $formRow = $form.find(`input[name="measurementContext|${contextId}"]`);
      } else if (modelId) {
        $formRow = $form.find(`input[name="measurementContext|${modelId}"]`);
      } else {
        console.error("Missing context or model id");
      }

      if (($formRow).is('[data-axis-right]')) {
        $chartRow.find('.js-axis-left').prop('checked', false);
        $chartRow.find('.js-axis-right').prop('checked', true);
        checkboxesChanged = true;
      }
    });

    if (checkboxesChanged) {
      updateChart($form);
    }
  });

  // Exclusive checkboxes on one row:
  $page.on('change', 'input.js-axis', function(e) {
    let $checkbox = $(e.currentTarget);
    let $other;

    if ($checkbox.is('.js-axis-left')) {
      $other = $checkbox.parents('.js-row').find('.js-axis-right');
    } else if ($checkbox.is('.js-axis-right')) {
      $other = $checkbox.parents('.js-row').find('.js-axis-left');
    }

    if ($checkbox.is(':checked')) {
      $other.prop('checked', false);
    } else {
      $other.prop('checked', true);
    }
  });

  $page.on('change', 'form.js-chart-form', function(e) {
    let $form = $(e.currentTarget);
    updateChart($form);
  });

  $page.on('click', '.js-select-all', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox].js-measurement-toggle:visible').prop('checked', true);

    updateChart($form)
  });

  $page.on('click', '.js-clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('.js-technique-row input[type=checkbox]').prop('checked', false);

    updateChart($form)
  });

  function updateChart($form) {
    let $chart = $form.find('.js-chart');

    let width          = Math.floor($chart.width());
    let scrollPosition = $(document).scrollTop();

    return $.ajax({
      url: `/comparison/chart?width=${width}`,
      dataType: 'html',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        $chart.html(response);
        $(document).scrollTop(scrollPosition);
      }
    })
  }
});
