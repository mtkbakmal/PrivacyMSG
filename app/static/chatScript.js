// Отображаем имя пользователя при загрузке
const username = localStorage.getItem('chat_username') || 'Guest';
document.getElementById('user-display').innerText = `@${username}`;

async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST', // Используем POST, как и в Python
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            localStorage.removeItem('chat_username', username)
            window.location.href = '/auth'; // Возврат на страницу логина
            alert("Вы вышли из системы")
        } else {
            alert("Ошибка при выходе из системы")
        }

    } catch (error) {
        console.error("Ошибка сети:", error);
    }
}

document.getElementById('message-form').onsubmit = (e) => {
    e.preventDefault();
    const input = document.getElementById('msg-input');
    if (!input.value.trim()) return;

    const msgArea = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'msg outgoing';
    msgDiv.innerText = input.value;
    msgArea.appendChild(msgDiv);

    input.value = '';
    msgArea.scrollTop = msgArea.scrollHeight;
};