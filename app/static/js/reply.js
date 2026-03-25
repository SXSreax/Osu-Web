document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.querySelector(".comment-input-wrapper textarea");

  function autoExpand(el) {
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";
  }

  autoExpand(textarea);

  textarea.addEventListener("input", function () {
    autoExpand(this);
  });
});
