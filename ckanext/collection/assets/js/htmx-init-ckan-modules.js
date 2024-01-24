$(document).ready(function () {

    // initialize CKAN modules for HTMX loaded pages
    htmx.on("htmx:afterSettle", function (event) {
        var elements = event.target.querySelectorAll("[data-module]");
        for (let node of elements) {
            ckan.module.initializeElement(node);
        }
    });
})
