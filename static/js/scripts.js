function clearAllAlerts() {
    var alerts = document.getElementsByClassName('alert');
    while (alerts[0]) {
        alerts[0].parentNode.removeChild(alerts[0]);
    }
}
