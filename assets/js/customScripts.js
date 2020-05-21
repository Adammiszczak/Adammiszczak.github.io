let navToggler = document.querySelector("span.navbar-toggle");
let navMenu = document.querySelector("ul.navbar-list");

navToggler.addEventListener("click", () => {
    navMenu.classList.toggle("visible")
})

