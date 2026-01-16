// This function attaches events to "compare" and "uncompare" buttons on the
// given page container. These require buttons with specific classes to be
// present on the page.
//
// The global `document` is accessed to get the currently stored ids to compare
// and to update the sidebar UI.
//
function initCompareButtons($page) {
  let $compareData = $(document).find('[data-compare-ids]')

  let compareIds;
  if ($compareData.length > 0) {
    compareIds = new Set($compareData.data('compareIds').toString().split(','));
  } else {
    compareIds = new Set();
  }

  let studyId = $page.data('studyId');

  $page.find('.js-compare-container').each(function() {
    let $container = $(this);
    if (!$container.data('contextIds')) {
      return;
    }

    let ids = new Set($container.data('contextIds').toString().split(','));
    if (!ids.isSubsetOf(compareIds)) {
      return;
    }

    $container.find('.js-uncompare').removeClass('hidden');
    $container.find('.js-compare').addClass('hidden');
    $container.parents('.js-table-row').addClass('highlight');
  });

  $page.on('click', '.js-compare a', function(e) {
    e.preventDefault();

    let $button    = $(this);
    let $wrapper   = $button.parents('.js-compare');
    let $container = $button.parents('.js-compare-container');

    let contextIds = [];
    let modelIds   = [];

    if ($container.data('contextIds')) {
      contextIds = $container.data('contextIds').toString().split(',');
    }
    if ($container.data('modelIds')) {
      modelIds = $container.data('modelIds').toString().split(',');
    }

    updateCompareData('add', contextIds, modelIds, function(compareData) {
      // Hide "compare" button, show "uncompare" button
      $wrapper.addClass('hidden');
      $container.find('.js-uncompare').removeClass('hidden');

      // Highlight compared row
      $container.parents('.js-table-row').addClass('highlight');
    });
  });

  $page.on('click', '.js-uncompare a', function(e) {
    e.preventDefault();

    let $button    = $(this);
    let $wrapper   = $button.parents('.js-uncompare');
    let $container = $button.parents('.js-compare-container');

    let contextIds = $container.data('contextIds').toString().split(',');
    let modelIds   = $container.data('modelIds').toString().split(',');

    updateCompareData('remove', contextIds, modelIds, function(compareData) {
      // Hide "uncompare" section, show "compare" button
      $wrapper.addClass('hidden');
      $container.find('.js-compare').removeClass('hidden');

      // Unhighlight previously compared row
      $container.parents('.js-table-row').removeClass('highlight');
    });
  });
}

// This function makes an ajax request to update the "compare data" stored in
// the session.
//
function updateCompareData(action, contexts, models, successCallback) {
  $.ajax({
    type: 'POST',
    url: `/comparison/update/${action}.json`,
    data: JSON.stringify({'contexts': contexts, 'models': models}),
    cache: false,
    contentType: 'application/json',
    processData: true,
    success: function(response) {
      let compareData = JSON.parse(response);
      let recordCount = compareData.contextCount + compareData.modelCount;

      if (recordCount > 0) {
        countText = `(${compareData.contextCount + compareData.modelCount})`;
      } else {
        countText = '';
      }

      let $sidebarCompareItem = $(document).find('.js-sidebar-compare');
      $sidebarCompareItem.find('.js-count').html(countText);

      $sidebarCompareItem.addClass('highlight');
      setTimeout(function() {
        $sidebarCompareItem.removeClass('highlight');
      }, 500);

      successCallback(compareData)
    },
  })
}
