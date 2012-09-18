Python SublerCLI wrapper
---

- pySubler является быстрой и удобной обёрткой над SublerCLI в OS X.
- http://gleero.com/all/pysubler/

Установка:
---

    git clone git://github.com/gleero/Subler.git
    cd Subler
    python setup.py install

Пример:
---

    from pySubler import Subler
    obj = Subler()
    obj.Source("inception.mkv")
    obj.Dest("inception.m4v")
    obj.AddArtwork("~/Images/inception.jpg")
    obj.Name = "Inception"
    obj.Artist = "Christopher Nolan"
    obj.Save()


Поиск SublerCLI:
---

pySubler – достаточно умная библиотека, чтобы попытаться самостоятельно найти SublerCLI. Искать будет сначала в системе, потом в `SublerCLIPath`. По-умолчанию `SublerCLIPath = "."`, тоесть искать будет в рабочем каталоге. Можно напрямую в конструкторе указать место поиска (как каталог, так и полный путь к бинарнику).

    obj = Subler(SublerCLIPath = "~/my/bin/SublerCLI")

или

    obj = Subler(SublerCLIPath = "~/opt/bin/")

Асинхронная работа:
---

Так как перепаковка больших файлов занимает некоторое время, то была добавлена возможность асинхронной работы.

    def Complete(data):
        print "Я всё!"

    s = Subler()
    s.onFinish += Complete
    s.Save(acync=True)

Классы:
---
Для упрощения разработки имеются классы-перечисления:

MediaTypes:
-
Типы медиаданных iTunes

ContentRatings:
-
Виды контент-рейтингов

Ratings:
-
Виды рейтингов

Методы:
---

Save:
-
Применяем зменения, сохраняем файл. Вызывается после всех остальных методов.
    obj.Save()
Можно асинхронно:
    obj.Save(acync=True)

Source:
-
Файл, который мы хотим конвертировать. Подходят форматы mp4, m4v, mkv.
    obj.Source("from.mkv")

Dest:
-
Файл, куда будем сохранять результаты. Формат – m4v либо mp4.
    obj.Source("to.m4v")

Optimize:
-
Оптимизация файла путём переноса moov-заголовка в начало файла.
    obj.Optimize()

Downmix:
-
Даунмикс аудио (mono, stereo, dolby, pl2) из исходника.
    obj.Downmix()

AddArtwork:
-
    Добавить обложку к видео-файлу.
    obj.AddArtwork("artwork.jpg")

Language:
-
Язык субтитров. По-умолчанию "English".
    obj.Language("Russian"):

Список свойств:
---

+ Name
+ Artist
+ AlbumArtist
+ Album
+ Grouping
+ Composer
+ Comments
+ Genre
+ TVShow
+ TVEpisode
+ TVNetwork
+ TVEpisodeID
+ TVSeason
+ Description
+ LongDescription
+ RatingAnnotation
+ Studio
+ Cast
+ Director
+ Codirector
+ Producers
+ Screenwriters
+ Lyrics
+ Copyright
+ EncodingTool
+ EncodedBy
+ contentID
+ HDVideo
+ Gapless
+ ContentRating (перечисление ContentRatings)
+ MediaKind (перечисление MediaTypes)
+ ReleaseDate
+ Track (массив из двух чисел, например: Трек 10/24)
+ Disk (массив из двух чисел, например: Диск 1/2)
+ Rating (перечисление Ratings)

Подробнее тут: http://code.google.com/p/subler/wiki/SublerCLIHelp

Полезное:
---

Если напечатать объект, то увидим все аргументы командной строки:

    >>> print obj

    /usr/local/bin/SublerCLI -metadata "{Artist:Christopher Nolan}{Name:Inception}" -source "inception.mkv" -dest "inception.m4v"

Чейнджлог:
---

1.0.2:
--
+ Теперь для назначения тегов вместо методов используются свойства.

1.0.1:
--
+ Проект переименован в pySubler, дабы избежать путаниц и обломов поисковиков;
+ Упрощен установщик, теперь модуль не является частью пакета;
+ Изменился импорт на from pySubler import Subler.