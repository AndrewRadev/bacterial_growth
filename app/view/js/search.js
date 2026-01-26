Page('.search-page', function($page) {
  // Initialize selection of strains
  let $strainSelect = $page.find('.js-strain-select');
  $strainSelect.select2({
    width: '100%',
    theme: 'custom',
    ajax: {
      url: '/strains/completion/?with-studies=1',
      dataType: 'json',
      delay: 150,
      cache: true,
      transport: select2TransportWithLoader($strainSelect),
    },
    templateResult: select2Highlighter,
  });

  // Initialize selection of metabolites
  $page.find('.js-metabolite-select').each(function() {
    let $select = $(this);

    $select.select2({
      multiple: true,
      theme: 'custom',
      width: '100%',
      ajax: {
        url: '/metabolites/completion/?with-studies=1',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter,
    });

    $select.trigger('change');
  });

  // Trigger search automatically
  $page.on('keyup', 'input[name=q]', _.debounce(updateSearch, 200));
  $page.on('change', '.js-strain-select,.js-metabolite-select', updateSearch)
  $page.on('change', '.js-per-page', updateSearch)

  // Make sure the "advanced search" checkbox reflects the current state of the
  // form:
  let $checkbox = $page.find('#advanced-search-input');
  let $inputs = $checkbox.parents('.form-row').nextAll('.form-row.clause');
  if ($inputs.length == 0) {
    $checkbox.prop('checked', false);
  } else {
    $checkbox.prop('checked', true);
  }

  $page.on('click', '.js-load-more', function(e) {
    e.preventDefault();
    loadNextPage($(this));
  });

  /*
   * Advanced search:
   */

  $page.on('click', '.js-add-clause', function(e) {
    e.preventDefault();

    $button = $(e.currentTarget);
    let new_clause = buildNewClause();
    $button.parents('.form-row').before(new_clause);
  });

  $page.on('click', '.js-remove-clause', function(e) {
    e.preventDefault();

    $clause = $(e.currentTarget).parents('.form-row.clause');
    $clause.remove();
  });

  function updateSearch() {
    let $searchForm  = $page.find('.js-search-form');
    let $resultsList = $page.find('.js-results-list');

    $resultsList.addClass('loading');

    $searchForm.ajaxSubmit({
      success: function(response) {
        $resultsList.html(response);
        $resultsList.removeClass('loading');
      }
    });
  }

  function loadNextPage($button) {
    let offset = $page.find('.js-search-result').length;
    let $searchForm  = $page.find('.js-search-form');

    $button.addClass('loading');

    $searchForm.ajaxSubmit({
      urlParams: { offset },
      success: function(response) {
        $button.replaceWith(response);
      }
    });
  }

  function buildNewClause() {
    let template_clause = $page.find('#form-clause-template').html();

    // We need to prepend all names and ids with "clause-N" for uniqueness:
    let clause_index = $page.find('.form-row.clause').length;
    template_clause = template_clause.replaceAll('name="', `name="clauses-${clause_index}-`);
    template_clause = template_clause.replaceAll('id="', `id="clauses-${clause_index}-`);

    return template_clause;
  }
});
