const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

setTimeout(function() {
    const alertList = document.querySelectorAll('.alert');
    const alerts = [...alertList].map((element) =>
    {
        const alert = new bootstrap.Alert(element);
        alert.close();
    })
}, 5000);

const hash = window.location.hash.split('/');
const hash_route = hash[0];
const hash_arg = hash[1];

switch (hash_route) {
    case "#popup":
        const modal = new bootstrap.Modal('#' + hash_arg);
        modal.show();
    break;

    default:
        break;
}