"use strict";
(function () {
    if (typeof window.CustomEvent === "function") return false;

    function CustomEvent(event, params) {
        params = params || { bubbles: true, cancelable: true, detail: undefined };
        var evt = document.createEvent('submit');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    }

    CustomEvent.prototype = window.Event.prototype;

    window.CustomEvent = CustomEvent;

})();
let tabForm = document.getElementById("tabForm");
let evt = new CustomEvent("submit", { "bubbles": true, "cancelable": true });
function onTabClick(tab) {
    tabForm.action = tab.getAttribute("value");
    tabForm.dispatchEvent(evt);
}
function addCaptcha(e) {
    e.preventDefault();
    grecaptcha.ready(function () {
        grecaptcha.execute('6LeKlDAgAAAAAIhaze6cgUF-ZRk7SAHPYo3w8a7R', { action: 'submit' }).then(function (token) {
            document.getElementsByName("gcaptcha")[0].value = token;
            subform.submit();
        });
    })
};
if (tabForm) {
    let tabs = document.getElementsByClassName("tab");
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].addEventListener("click", onTabClick.bind(null, tabs[i]), false);
    }
}

let subform = document.getElementById("subform") || tabForm;
if (subform) {
    subform.addEventListener("submit", addCaptcha);
}