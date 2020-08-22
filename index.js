

/* Message navigation */
var $mh = $(".message-heading");
$mh.click(function(ev){$(ev.target).removeClass("highlight")})
var $curr = null;
function highlight($elem) {
   $elem.addClass("highlight");
}
function stop_highlight($elem) {
   $elem.removeClass("highlight");
}
function on_hash_change(){
   if ($curr !== null) {
      stop_highlight($curr);
   }
   $curr = $(window.location.hash);
   highlight($curr);
}
$(window).on("hashchange", on_hash_change)

/* Top button */

$top = $("#up-button");
$top.click(function(){
   var ind = window.location.href.lastIndexOf("#");
   window.history.replaceState(null,"", window.location.href.substring(0, ind));
   window.scrollTo(0,0);
});

on_hash_change()

