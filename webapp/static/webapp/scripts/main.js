"use strict"
let tabForm = document.getElementById("tabForm");
function onTabClick(tab) {
    tabForm.action = tab.getAttribute("value");
    tabForm.submit();
}
if (tabForm) {
    let tabs = document.getElementsByClassName("tab");
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].addEventListener("click", onTabClick.bind(null, tabs[i]), false);
    }
}