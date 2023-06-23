const passwordField = document.querySelector("#passwordField");
const confirmPasswordField = document.querySelector("#confirmPasswordField");
const showPasswordToggle = document.querySelector(".showPasswordToggle");

const handleToggleInput = (e) => {
  if (showPasswordToggle.textContent === "SHOW") {
    showPasswordToggle.textContent = "HIDE";
    passwordField.setAttribute("type", "text");
    confirmPasswordField.setAttribute("type", "text");
  } else {
    showPasswordToggle.textContent = "SHOW";
    passwordField.setAttribute("type", "password");
    confirmPasswordField.setAttribute("type", "password");
  }
};

showPasswordToggle.addEventListener("click", handleToggleInput);
