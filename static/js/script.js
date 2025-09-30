document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function(e) {
            const nombre = form.nombre.value.trim();
            const email = form.email.value.trim();
            if (!nombre || !email) {
                alert("Por favor, completa todos los campos.");
                e.preventDefault();
            }
        });
    }
});
