const usernameField = document.querySelector("#usernameField");
const feedbackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedbackArea = document.querySelector(".emailFeedbackArea");
const passwordField = document.querySelector("#passwordField");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const emailSuccessOutput = document.querySelector(".emailSuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const submitButton = document.querySelector(".submit-btn");

submitButton.disabled = true;

const handleToggleInput = (e) => {
  if (showPasswordToggle.textContent === "SHOW") {
    showPasswordToggle.textContent = "HIDE";
    passwordField.setAttribute("type", "text");
  } else {
    showPasswordToggle.textContent = "SHOW";
    passwordField.setAttribute("type", "password");
  }
};

usernameField.addEventListener("keyup", (e) => {
  const usernameVal = e.target.value;
  usernameSuccessOutput.style.display = "block";
  usernameSuccessOutput.textContent = `Checking ${usernameVal}`;

  usernameField.classList.remove("is-invalid");
  feedbackArea.style.display = "none";
  feedbackArea.innerHTML = "";

  if (usernameVal.length > 0) {
    fetch("/authentication/validate-username", {
      body: JSON.stringify({ username: usernameVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        usernameSuccessOutput.style.display = "none";
        if (data.username_error) {
          submitButton.disabled = true;
          usernameField.classList.add("is-invalid");
          feedbackArea.style.display = "block";
          feedbackArea.innerHTML = `<p>${data.username_error}</P>`;
        } else {
          submitButton.removeAttribute("disabled");
        }
      });
  } else {
    usernameSuccessOutput.style.display = "none";
  }
});

emailField.addEventListener("keyup", (e) => {
  const emailVal = e.target.value;
  emailSuccessOutput.style.display = "block";
  emailSuccessOutput.textContent = `Checking ${emailVal}`;

  emailField.classList.remove("is-invalid");
  emailFeedbackArea.style.display = "none";
  emailFeedbackArea.innerHTML = "";

  if (emailVal.length > 0) {
    fetch("/authentication/validate-email", {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        emailSuccessOutput.style.display = "none";
        if (data.email_error) {
          submitButton.disabled = true;
          emailField.classList.add("is-invalid");
          emailFeedbackArea.style.display = "block";
          emailFeedbackArea.innerHTML = `<p>${data.email_error}</P>`;
        } else {
          submitButton.removeAttribute("disabled");
        }
      });
  } else {
    emailSuccessOutput.style.display = "none";
  }
});

showPasswordToggle.addEventListener("click", handleToggleInput);
