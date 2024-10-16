document.addEventListener('DOMContentLoaded', function() {
    
    document.getElementById('submitLogin').addEventListener('click', function(event) {
        var password = document.getElementById('inputPassword').value;
        var email = document.getElementById('inputEmail').value;

        loginUsuario(event, password, email);
    });
    function loginUsuario(event, password, email) {
        event.preventDefault();
        var formData = new FormData();
        formData.append('password', password);
        formData.append('email', email);

        fetch('/login', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.login) {
                window.location.href = "/home";
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error(error);
        });
    }
});