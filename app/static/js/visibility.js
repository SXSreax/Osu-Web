document.addEventListener("DOMContentLoaded", function () {
  const passwordInput =
    document.getElementById("password") ||
    document.getElementById("new_password");
  const passwordToggle = document.getElementById("password-toggle");
  const icon = passwordToggle.querySelector(".password-toggle-icon");

  if (!passwordInput || !passwordToggle || !icon) {
    return;
  }

  passwordToggle.addEventListener("click", function () {
    const isPassword = passwordInput.type === "password";

    passwordInput.type = isPassword ? "text" : "password";

    passwordToggle.setAttribute(
      "aria-label",
      isPassword ? "Hide password" : "Show password",
    );

    passwordToggle.title = isPassword ? "Hide password" : "Show password";

    icon.src = isPassword
      ? "/static/images/hide.png"
      : "/static/images/show.png";
  });
});
