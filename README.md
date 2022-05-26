# Yandex Lyceum Docs
### Скрипт для удобного представления документации по любым курсам на платформе **Академии Яндекса**

<details>
  <summary>Скриншоты</summary>

![Courses_Page](https://user-images.githubusercontent.com/67208948/169401617-61e65220-09fc-40af-b6c8-a180538d1b1c.png)
![Lessons_Page](https://user-images.githubusercontent.com/67208948/169401794-400cdb54-f51f-456d-872b-3a256873b98a.png)
![Lesson Page](https://user-images.githubusercontent.com/67208948/169401888-6525a357-983e-4562-824b-c710a66d7478.png)
![Task Page](https://user-images.githubusercontent.com/67208948/169401972-28d901ea-27c9-4a8e-8e26-268bc3efa652.png)
![Material Page](https://user-images.githubusercontent.com/67208948/169402055-a06f8a85-eac6-45b6-9bef-fd5ff025d494.png)

</details>

## Использование
* Перед началом необходимо проверить аккаунт Яндекса: вход должен быть только по паролю.
  * Перейти в [настройки профиля](https://passport.yandex.ru).
  * Найти пункт **Пароли и авторизация** -> **Способ входа**.
  * Выбрать **"Вход с паролем"**.
    <details>
    <summary>Скриншот</summary>

    ![Courses_Page](https://user-images.githubusercontent.com/70765138/170548269-2c22fc24-4dde-42db-8bc4-098ebc2b4135.jpeg)
    
    </details>
  
  
* Клонируем [репозиторий](https://github.com/fast-geek/YandexLyceumDocs)
```shell
git clone https://github.com/fast-geek/YandexLyceumDocs.git
```
* Переходим в каталог репозитория и устанавливаем зависимости
```shell
cd YandexLyceumDocs
pip install -r requirements.txt
```
* Запускаем программу с логином и паролем аккаунта Yandex 
  * Аргументы `--materials` и `--solutions` используются для загрузки материалов и решений (Опционально)
  * Аргумент `--teacher` используется для скачивания курсов в режиме учителя (Опционально)
```shell
python -m generator --login "YANDEX_USERNAME" --password "YANDEX_PASSWORD" --materials --solutions
```
* Выбираем необходимые курсы и ждём окончания работы программы
* Переходим в новую папку `docs` и запускаем статический сервер Python
```shell
cd docs
python -m http.server 8000
```
* Переходим на [localhost:8000](http://localhost:8000)

## Примечание
Любые материалы, полученные с помощью Yandex Lyceum Docs разрешается использовать только в личных целях.
Распространение, публикация материалов запрещена в соответствии с пользовательским соглашением Академии Яндекса.
> Исключительное право на учебную программу и все сопутствующие ей учебные материалы, доступные в рамках проекта «Лицей Академии Яндекса», принадлежат АНО ДПО «ШАД». Воспроизведение, копирование, распространение и иное использование программы и материалов допустимо только с предварительного письменного согласия АНО ДПО «ШАД».
> [Пользовательское соглашение](https://yandex.ru/legal/lms_termsofuse/)
