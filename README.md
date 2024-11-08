# EduQueue
[Презентация](https://docs.google.com/presentation/d/1BtuUGJ2eM8Oyx3UbGKW-v-Lhr0beBV9Y/edit#slide=id.p1)

Часто при записи в очередь на защиту лабораторных методика "кто первый встал -- того и тапки" кажется несправедливой. В целях решения этой проблемы предлагается Telegram-бот, в котором преподаватель может создавать очереди на сдачу с кастомными приоритетами.  
Функциональность со стороны преподавателя включает в себя:
* Создать группу + сгенерировать инвайт-код для вступления
* Задать кол-во лабораторных работ в группе
* Задать дедлайны по лабораторным работам
* Исключить студента из группы
* Создать очередь защиты, указав её имя, дату и время и установив приоритет
* Удалить очередь
* Отредактировать очередь
* Взять человека из очереди, отметить сдал/не сдал, отметить окончание сдачи
* Добавить новое правило сортировки к уже имеющимся
* Правило сортировки представляет из себя список параметров, расположенных по убыванию значимости.

Пример: Если задано правило сортировки ["Пропущен ли дедлайн по сдаваемой лабораторной", "Номер лабораторной", "Кол-во нарушенных дедлайнов"], то раньше пойдут студенты, у которых не пропущен дедлайн, по убыванию номера лабораторной, а при равном номере - те, кто пропустил меньше дедлайнов.  
  
В свою очередь, студент может:
* Присоединиться к группе
* Выйти из группы
* Получать уведомления о начале записи
* Записаться на сдачу
* Выписаться из сдачи
* Посмотреть очереди
* Посмотреть правила очереди

## Сборка

Подсказки по сборке

### Команда для установки зависимостей

Чтобы установить все необходимые завивсимости, нужно перейти в корень репозитория и выполнить следущую команду:
```sh
pip install .
# or if it does not work, try `python -m pip install .`
```

### Команда для запуска

После установки завивисимостей бота можно запустить следующей командой:
```sh
main
```

### Команда для запуска тестов

```sh
# It will discower tests in specified packages
pytest
```

## Авторы

- Вячеслав Григорович
- Максим Вуколов
- Вадим Козлов
- Дмитрий Соколов
- Глеб Герлах
