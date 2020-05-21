let navToggler = document.querySelector("div.navbar-toggle");
let navMenu = document.querySelector("ul.navbar-list");

navToggler.addEventListener("click", () => {
    navMenu.classList.toggle("visible")
})

