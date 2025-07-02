$.fn.log = function() {
  console.log($(this));
  return this;
}

function wrapSubstrings(text, words, prefix, suffix) {
  if (words.length <= 0 || words[0].length <= 0) {
    return text;
  }

  let result         = "";
  let lowercaseText  = text.toLowerCase();
  let lowercaseWords = words.map((s) => s.toLowerCase());

  let currentWordIndex = 0;
  let query            = lowercaseWords[currentWordIndex];

  let previousTextIndex = 0
  let currentTextIndex  = lowercaseText.indexOf(query);

  if (currentTextIndex < 0) {
    return text;
  }

  while (currentTextIndex >= 0 && currentWordIndex < lowercaseWords.length) {
    result += text.substring(previousTextIndex, currentTextIndex);
    result += prefix + text.substring(currentTextIndex, currentTextIndex + query.length) + suffix;

    previousTextIndex = currentTextIndex + query.length;

    currentWordIndex += 1;
    query = lowercaseWords[currentWordIndex];

    currentTextIndex  = lowercaseText.indexOf(query, previousTextIndex + 1);
  }

  result += text.substring(previousTextIndex);

  return result;
}

function select2Highlighter(state) {
  $searchField = $('.select2-container--open .select2-search__field');

  let query = $.trim($searchField.val());
  let text = wrapSubstrings(
    state.text,
    query.split(/\s+/),
    '<span class="select2-highlight">',
    '</span>',
  );

  return $('<div>' + text + '</div>');
}

function select2TransportWithLoader($select) {
  return function (params, success, failure) {
    let request = $.ajax(params);
    let $select2container = $select.next('.select2-container');

    let $spinner = $select2container.find('.loading-spinner');
    if ($spinner.length == 0) {
      let $spinner = $("<span class='loading-spinner'></span>")
      $select2container.append($spinner);
    }

    request.then(function(...args) {
      $select2container.find('.loading-spinner').remove();
      success(...args)
    });
    request.fail(failure);

    return request;
  }
}
