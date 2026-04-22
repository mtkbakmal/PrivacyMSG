const authForm = document.getElementById('auth-form');
const emailInput = document.getElementById('email');
const authSubmitBtn = document.getElementById('auth-submit');
let currentMode = 'login';

function switchAuth(mode) {
    currentMode = mode;
    if (mode === 'register') {
        emailInput.classList.remove('hidden');
        emailInput.required = true;
        authSubmitBtn.innerText = 'Создать аккаунт';
        document.getElementById('tab-register').classList.add('active');
        document.getElementById('tab-login').classList.remove('active');
    } else {
        emailInput.classList.add('hidden');
        emailInput.required = false;
        authSubmitBtn.innerText = 'Войти';
        document.getElementById('tab-login').classList.add('active');
        document.getElementById('tab-register').classList.remove('active');
    }
}

authForm.onsubmit = async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = emailInput.value;

    const url = currentMode === 'login' ? '/login' : '/register';
    const body = currentMode === 'login' 
        ? { username, password } 
        : { username, password, email };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const result = await response.json();

        if (response.ok) {
            if (currentMode === 'register') {
                alert("Регистрация успешна! Теперь войдите.");
                switchAuth('login');
            } else {
                // Сохраняем имя пользователя для чата (например, в localStorage)
                localStorage.setItem('chat_username', username);
                // Перенаправляем на страницу чата
                window.location.href = '/chat'; 
            }
        } else {
            alert(result.detail || "Произошла ошибка");
        }
    } catch (error) {
        console.error("Ошибка запроса:", error);
        alert("Сервер не отвечает");
    }
};