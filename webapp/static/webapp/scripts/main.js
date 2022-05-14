"use strict"
let search_bar = document.getElementsByClassName("search-bar")[0];
if (search_bar) {
    search_bar.getElementsByClassName("search-btn")[0].addEventListener("click", () => {
        redirect(search_bar);
    });
    search_bar.getElementsByClassName("search-input")[0].addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            redirect(search_bar);
        }
    });
}
function isInstagramURL(url) {
    const regex = /https?:\/\/[\w\.]*instagram.com[\/\w_\-\?=&]*/i;
    return regex.test(url);
}
function redirect(search_bar) {
    let search_input = search_bar.getElementsByClassName("search-input")[0];
    if (!isInstagramURL(search_input.value)) {
        location.href = `./${search_input.value}`;
    }
    else {
        let url = new URL(search_input.value);
        let pathname = url.pathname;
        let splittedURL = pathname.split("/").filter((e) => e);
        let id = "";
        if (splittedURL.length !== 2) {
            id = splittedURL[0];
        } else {
            id = splittedURL[1];
        }
        location.href = `./${id}`;
    }
}