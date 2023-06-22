const searchField = document.querySelector("#expenseSearchField");
const searchTableOutput = document.querySelector(".table-output");
const appTableOutput = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tBodyContainer = document.querySelector(".table-output-body");

searchTableOutput.style.display = "none";

searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value;
  console.log(searchValue);

  if (searchValue.trim().length > 0) {
    paginationContainer.style.display = "none";
    tBodyContainer.innerHTML = "";
    fetch("/expenses/search", {
      body: JSON.stringify({ searchValue: searchValue.trim() }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        searchTableOutput.style.display = "block";
        appTableOutput.style.display = "none";
        if (data.length === 0) {
          tBodyContainer.innerHTML = "No results found";
        } else {
          data.forEach((item) => {
            tBodyContainer.innerHTML += `
            <tr>
            <td>${item.amount}</td>
            <td>${item.category}</td>
            <td>${item.description}</td>
            <td>${item.date}</td>
            </tr>
            `;
          });
        }
      });
  } else {
    searchTableOutput.style.display = "none";
    appTableOutput.style.display = "block";
    paginationContainer.style.display = "block";
  }
});
