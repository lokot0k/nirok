### 👑Команда: **«Гаражные Ковырялы»**
- [Яковлев Павел](https://t.me/poulyak) _(DS/AI/ML)_
- [Иван Королёв](https://t.me/korlivan) _(Backend,Frontend)_
- [Евгений Бекалдиев](https://t.me/sejapoe) _(Backend,Frontend)_
- [Любовь Ушакова](https://t.me/loveushakova) _(UX/UI)_
- [Егор Петерс](https://t.me/egorka_pomedorka) _(DS/AI/ML)_



### Задача: **Распознавание действий человека по видео**

- Ссылка на [колаб](https://colab.research.google.com/drive/18cRadmDBQ7hgqrRJrgShcYAiM2FIuvFh?usp=sharing) с обучением модели
- [Веса](https://drive.google.com/file/d/1JxRvHkkFIk8kcFdCUOC-McBdUuNY0bbd/view?usp=sharing) модели
- Конфигурационный [файл](model/mVitConfig.py)

Про тестирование и запуск модели [подробнее](model/README.md)
Обученные веса моделей также можно посмотреть в колабе


### Запуск сервиса для демонстрации модели
Для работы самой модели необходимо будет скачать checkpoint.pth по [ссылке](https://drive.google.com/file/d/1X69EA8GR0jGtLghiVThKa3Vp_yQpq4Pa/view?usp=sharing) и поместить его в папку /backend/static

Сам сервис развертывается одной командой в терминале:
```
docker-compose up
```
или
```
docker compose up
```
Затем потребуется подождать некоторое время (вплоть до ~15-ти минут при первом запуске), пока загрузятся и установятся все зависимости внутри докера.
После этого сервис можно будет открыть по адресу http://127.0.0.1:3000 