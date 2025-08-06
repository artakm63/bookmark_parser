document.addEventListener('DOMContentLoaded', () => {
    const categoryList = document.getElementById('category-list');
    const linkList = document.getElementById('link-list');
    const currentCategoryTitle = document.getElementById('current-category');
    const searchBox = document.getElementById('search-box');

    let allData = {};

    fetch('/data') // Обновленный путь
        .then(response => response.json())
        .then(data => {
            allData = data;
            renderCategories(allData);
            // По умолчанию отображаем первую категорию
            if (Object.keys(allData).length > 0) {
                const firstCategory = Object.keys(allData)[0];
                renderLinks(firstCategory, allData[firstCategory]);
                document.querySelector('#category-list li').classList.add('active');
            }
        });

    function renderCategories(data) {
        categoryList.innerHTML = '';
        for (const category in data) {
            const listItem = document.createElement('li');
            listItem.textContent = `${category} (${data[category].length})`; // Добавляем счетчик
            listItem.dataset.category = category;
            listItem.addEventListener('click', () => {
                renderLinks(category, data[category]);
                document.querySelectorAll('#category-list li').forEach(item => item.classList.remove('active'));
                listItem.classList.add('active');
            });
            categoryList.appendChild(listItem);
        }
    }

    function renderLinks(category, links) {
        currentCategoryTitle.textContent = category;
        linkList.innerHTML = '';
        links.forEach(item => {
            const linkItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = item.url;
            link.textContent = item.title || item.url;
            link.target = '_blank';

            const description = document.createElement('p');
            description.textContent = item.description || 'Нет описания';

            linkItem.appendChild(link);
            linkItem.appendChild(description);
            linkList.appendChild(linkItem);
        });
    }

    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const activeCategory = document.querySelector('#category-list li.active').dataset.category;
        
        if (!activeCategory) return;

        const filteredLinks = allData[activeCategory].filter(item => {
            const title = (item.title || '').toLowerCase();
            const url = (item.url || '').toLowerCase();
            return title.includes(searchTerm) || url.includes(searchTerm);
        });

        renderLinks(activeCategory, filteredLinks);
    });
});
