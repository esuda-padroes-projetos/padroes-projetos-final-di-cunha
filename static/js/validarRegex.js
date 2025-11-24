// Validação de email
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validarPlaca(placa) {
    const regex = /^[A-Z]{3}-?[0-9]{1}[A-Z0-9]{1}[0-9]{2}$/i;
    return regex.test(placa.replace(/\s/g, ''));
}

function validarCPF(cpf) {
    const regex = /^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$/;
    return regex.test(cpf.replace(/\D/g, '')) && cpf.replace(/\D/g, '').length === 11;
}

function validarFormularioCliente() {
    const email = document.getElementById("email").value;
    const cpf = document.getElementById("cpf").value;
    if (!validarEmail(email)) {
        alert("E-mail inválido!");
        return false;
    }
    if (!validarCPF(cpf)) {
        alert("CPF inválido! Use formato 123.456.789-00");
        return false;
    }
    return true;
}

function validarFormularioVeiculo() {
    const placa = document.getElementById("placa").value;
    if (!validarPlaca(placa)) {
        alert("Placa inválida! Ex: ABC-1234 ou ABC1D23");
        return false;
    }
    return true;
}