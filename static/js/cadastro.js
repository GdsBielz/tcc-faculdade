document.addEventListener('DOMContentLoaded', function() {
    // FUNÇÃO DO BOTÃO DE FINALIZAR CADASTRO (QUERO PARTICIPAR)
    document.getElementById('concluirCadastroBtn').addEventListener('click', function(event) {
        console.log("PASSEI AQUI");
        var nome = document.getElementById('nomeInput').value;
        var password = document.getElementById('passwordInput').value;
        var email = document.getElementById('emailInput').value;

        postCadastroNovoUsuario(event, nome, password, email);
    });

    // FUNÇÃO PARA CADASTRAR NOVO USUÁRIO
    function postCadastroNovoUsuario(event, nome, password, email) {
        event.preventDefault();
        const dataToSend = {
            nome: nome,
            password: password,
            email: email
        };
    
        fetch('/cadastro', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
        })
        .then(response => {
            if (!response.ok) {  // Verifica se o status não está na faixa de 200-299
                return response.json().then(errorData => {
                    throw new Error(errorData.message || 'Erro desconhecido');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Resposta recebida:', data);
            alert(data.message);
            window.location.href = "/login";
        })
        .catch(error => {
            console.error('Ocorreu um erro:', error);
            alert(error.message);
        });
    }
    
});