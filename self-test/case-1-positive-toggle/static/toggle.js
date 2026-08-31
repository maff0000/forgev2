// Toggles the details panel's native `hidden` attribute on button click.
document.addEventListener("DOMContentLoaded", function () {
  var button = document.getElementById("toggle-button");
  var panel = document.getElementById("details-panel");

  button.addEventListener("click", function () {
    var willBeHidden = !panel.hidden;
    panel.hidden = willBeHidden;
    button.setAttribute("aria-expanded", String(!willBeHidden));
    button.textContent = willBeHidden ? "Show details" : "Hide details";
  });
});
