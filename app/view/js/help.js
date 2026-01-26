Page('.help-page-index', function($page) {
  let $pageListContainer = $page.find('.js-page-list-container');
  let $searchInput = $('.js-search-input');

  if ($searchInput.val().trim().length > 0) {
    updatePage($searchInput);
  }

  $page.on('keyup', '.js-search-input', _.debounce(function() {
    let $searchInput = $(this);
    updatePage($searchInput);
  }, 100));

  function updatePage($searchInput) {
    let $form = $searchInput.parents('form');
    $pageListContainer.addClass('loading');

    $form.ajaxSubmit({
      success: function(response) {
        $pageListContainer.html(response);
        $pageListContainer.removeClass('loading');
      }
    });
  }
});

Page('.help-page', function($page) {
  renderMathInElement($page[0]);
});
