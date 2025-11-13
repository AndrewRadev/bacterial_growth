Page('.help-page-index', function($page) {
  let $pageList = $page.find('.js-page-list');
  let $searchInput = $('.js-search-input');

  if ($searchInput.val().length >= 0) {
    updatePage($searchInput);
  }

  $page.on('keyup', '.js-search-input', _.debounce(function() {
    let $searchInput = $(this);
    updatePage($searchInput);
  }, 100));

  function updatePage($searchInput) {
    let $form = $searchInput.parents('form');
    $pageList.addClass('loading');

    $form.ajaxSubmit({
      success: function(response) {
        $pageList.html(response);
        $pageList.removeClass('loading');
      }
    });
  }
});
