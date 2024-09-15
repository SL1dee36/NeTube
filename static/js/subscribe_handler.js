document.querySelector('#subscribe-button').addEventListener('click', function() {
    const userId = this.dataset.userId;
    const isSubscribed = this.innerText === 'Отписаться';

    fetch(isSubscribed ? `/api/unsubscribe/${userId}` : `/api/subscribe/${userId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Обновляем текст кнопки и ее цвет в зависимости от состояния подписки
            this.innerText = data.subscribed ? 'Отписаться' : 'Подписаться';

            // Обновляем цвет кнопки
            if (data.subscribed) {
                this.classList.add('bg-gray-200', 'text-gray-600', 'border-gray-300');
                this.classList.remove('bg-red-500', 'text-white', 'border-red-500');
            } else {
                this.classList.add('bg-red-500', 'text-white', 'border-red-500');
                this.classList.remove('bg-gray-200', 'text-gray-600', 'border-gray-300');
            }

            // Обновляем количество подписчиков
            const subscribersSpans = document.querySelectorAll('.subscribers');
            subscribersSpans.forEach(span => {
                span.innerText = data.subscribers + ' подписчиков';
            });
        } else {
            console.error(data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
});
