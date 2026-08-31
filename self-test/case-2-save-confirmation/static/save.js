// Triggers the persist on Save button click. Surfacing a confirmation to
// the user is a later increment's scope — this file only fires the save
// request; it does not read or act on the response.
document.addEventListener("DOMContentLoaded", function () {
  var button = document.getElementById("save-button");
  var input = document.getElementById("note-input");

  button.addEventListener("click", function () {
    fetch("/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note: input.value })
    });
  });
});
