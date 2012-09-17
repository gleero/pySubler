#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
SublerCLI wrapper v1.0
gleero@gmail.com
http://gleero.com/
'''


import os, subprocess
import datetime
from threading import Thread
import time


# Эмуляция событий
class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler


# Типы медиаданных iTunes
class MediaTypes():

    Music = "Music"
    Audiobook = "Audiobook"
    MusicVideo = "Music Video"
    Movie = "Movie"
    TVShow = "TV Show"
    Booklet = "Booklet"
    Ringtone = "Ringtone"


# Виды контент-рейтингов
class ContentRatings():

    No = "None"
    Clean = "Clean"
    Explicit = "Explicit"


# Виды рейтингов
class Ratings():

    Unrated = "Unrated"

    # Рейтинги США
    NR = "Not Rated"
    G = "G"
    PG = "PG"
    PG13 = "PG-13"
    R = "R"
    NC17 = "NC-17"

    TVY = "TV-Y"
    TVY7 = "TV-Y7"
    TVG = "TV-G"
    TVPG = "TV-PG"
    TV14 = "TV-14"
    TVMA = "TV-MA"

    # Рейтинги Британии
    U = "U"
    Uc = "Uc"
    _12 = "12"
    _12A = "12A"
    _15 = "15"
    _18 = "15"
    R18 = "R18"
    Exempt = "Exempt"
    Caution = "Caution"

    # Рейтинги Германии
    FSK0 = "FSK 0"
    FSK6 = "FSK 6"
    FSK12 = "FSK 12"
    FSK16 = "FSK 16"
    FSK18 = "FSK 18"


# Собственно, сублер
class Subler():

    # Полный путь к сублеру. Ищет сам, но можно и помочь указав в конструкторе прямой путь к SublerCLI, либо бросить его в корень программы
    SublerPath = None

    # Список мета-тегов, которые будут в свойстве "-metadata"
    MetaTags = {}

    # Аргументы командной строки
    Args = ""


    # При конвертации в строку объекта будем возвращать аргументы, которые намутили
    def __str__(self):

        return self.Args


    # Для динамических методов мета-тегов. Вся движуха в __dispatch
    def __getattr__(self, key):

        try:
            return object.__getattr__(self, key)
        except AttributeError:
            return self.__dispatch(key)


    # Конструктор. Инициализируем события и ищем сублера
    def __init__(self, SublerCLIPath="."):

        # Событие на завершение работу. Удобно применять с acync=True в методе Save()
        self.onFinish = EventHook()

        # Пытаемся найти SublerCLI средствами ОС.
        if bool(os.system("which %s > /dev/null" % "SublerCLI")):

            # Теперь пытаемся найти в SublerCLIPath. Если прямой путь прописан - замечательно. Если папка, то тоже неплохо. По-умолчанию ищем в корне
            if os.path.isfile(SublerCLIPath) and os.path.exists(SublerCLIPath):
                self.SublerPath = SublerCLIPath
            else:
                searchFile = os.path.join(SublerCLIPath, "SublerCLI")
                if os.path.exists(searchFile):
                    self.SublerPath = searchFile

                # Вообще нигде ничего не нашли.
                raise Exception("Программа `SublerCLI` не установлена! Ищите её на http://code.google.com/p/subler/downloads/list")
        else:
            # Нашли средствами ОС, сообщаем полный путь
            self.SublerPath = subprocess.check_output(["which", "SublerCLI"]).strip()


    # Динамические методы для метаданных
    def __dispatch(self, key):

        # Суть: есть список метатегов. Делаем из них список методов, убирая решетки и пробелы.
        # Пример: 
        #    obj.Track(1, 20) выдаст {Track #:1/20}
        #    obj.TVShow("House M. D.") выдаст {TV Show:House M. D.}
        # Всё просто.
        # Про метаданные тут: http://code.google.com/p/subler/wiki/SublerCLIHelp

        metadatas = ["Name", "Artist", "Album Artist", "Album", "Grouping", "Composer", "Comments", "Genre", "TV Show", "TV Episode #", "TV Network",
            "TV Episode ID", "TV Season", "Description", "Long Description", "Rating Annotation", "Studio", "Cast", "Director", "Codirector",
            "Producers", "Screenwriters", "Lyrics", "Copyright", "Encoding Tool", "Encoded By", "contentID", "HD Video", "Gapless", "Content Rating",
            "Media Kind", "Release Date", "Track #", "Disk #", "Rating"]

        # Названия методов: Всё то же самое, только без решеток и пробелов
        methods = [ x.replace("#", "").replace(" ", "") for x in metadatas ]

        # Ищем запрошенный метод среди списка возможных
        if key in methods:

            def default(*args):

                # Большинство тегов просто текстовые, но есть исключения:
                # Release Date должен содержать данные в формате YYYY-MM-DD
                # TV Episode ID может быть только числовой
                # Теги Track # и Disk # должны содержать данные в виде "#/#", поэтому упрощаем апи и делаем два аргумента

                if len(args) == 1:

                    # Для большинства текстовых тегов
                    rets = args[0]

                    # Проверка дополнительных условий

                    # Дата релиза должна соответствовать маске YYYY-MM-DD, поэтому принимает только datetime объект. Ибо нехуй
                    if key == "ReleaseDate":
                        if args[0].__class__.__name__ == "date":
                            rets = args[0].strftime('%Y-%m-%d')
                        else:
                            raise Exception("Метод `%s.%s` принимает только объект `datetime`!" % (self.__class__, key))

                    # ID эпизода должен быть только числовой
                    if key == "TVEpisodeID":
                        if not str(args[0]).isdigit():
                            raise Exception("Метод `%s.%s` принимает только число!" % (self.__class__, key))

                    # Добавляем тег и значение
                    self.MetaTags[metadatas[methods.index(key)]] = rets

                # Те самые Track и Disk с двумя аргументами
                elif len(args) == 2:

                    if key == "Track" or key == "Disk":
                        rets = "%s/%s" % (args[0], args[1])
                    else:
                        raise Exception("Только методы `Track` и `Disk` принимают 2 аргумента.")

                    # Добавляем тег и значение
                    self.MetaTags[metadatas[methods.index(key)]] = rets

                # Число аргументов вообще не то
                else:
                    raise Exception("Неверное количество аргументов в `%s.%s`!" % (self.__class__, key))

            return default


    # Сохраняем новый файл. Можно асинхронно! Тогда лучше подписаться на событие onFinish
    # Тут проверяем всё, что насоставляли и генерируем аргументы командной строки сублера
    def Save(self, acync=False):

        # Если источник либо назначение не указаны, то нет смысла что-либо делать
        if not hasattr(self, 'sourceFile') or not hasattr(self, 'destFile'):
            raise Exception("Источник либо назначение не определены!")

        # Готовим аргументы командной строки
        self.Args = self.SublerPath

        # Мета-теги
        tags = ""
        for index, tag in self.MetaTags.items():
            tags += "{%s:%s}" % (index, tag)
        if tags != "":
            self.Args += " -metadata \"%s\"" % tags

        # Оптимизация
        if hasattr(self, 'optimize') and self.optimize:
            self.Args += " -optimize"

        # Язык
        if hasattr(self, 'language') and self.language:
            self.Args += " -language \"%s\"" % self.language

        # Даунмикс
        if hasattr(self, 'downmix') and self.downmix:
            self.Args += " -downmix"

        # Источник и назначение
        self.Args += " -source \"%s\" -dest \"%s\"" % (self.sourceFile, self.destFile)

        # Запускаем конвертацию. Можно асинхронно. А можно и нет. Аки полная свобода выбора
        if acync:
            t = Thread(target=self.__run)
            t.daemon = True
            t.start()

        else:
            self.__run()


    # Файл, который мы хотим конвертировать
    def Source(self, sourceFile):

        self.sourceFile = self.__AbsPath(sourceFile)


    # Файл, куда будем сохранять результаты
    def Dest(self, destFile):

        self.destFile = destFile


    # Оптимизация файла путём переноса moov-заголовка в начало файла
    def Optimize(self):

        self.optimize = True


    # Даунмикс аудио (mono, stereo, dolby, pl2) из исходника
    def Downmix(self):

        self.downmix = True


    # Добавляем обложку к видео
    def AddArtwork(self, artwork):

        artwork = self.__AbsPath(artwork)
        self.MetaTags['Artwork'] = artwork


    # Язык субтитров. По-умолчанию "English"
    def Language(self, language):

        self.language = language


    # Запускаем конвертацию
    def __run(self):

        # Стартуем процесс в шелле, вывод перенаправляем, чтобы после окончания работы посмотреть результат
        process = subprocess.Popen(self.Args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
        rawdata = ""
        # Читаем всё
        while process.poll() is None:
            output = process.stdout.readline()
            errors = process.stderr.readline()
            rawdata += output + "\n" + errors + "\n"
        # Ждём завершения процесса
        process.wait()
        # Вызываем событие onFinish и передаём туда всё, что получили в поток вывода
        self.onFinish.fire(rawdata)


    # Проверят существование файла и возвращает абсолютное имя
    def __AbsPath(self, fname):

        if not os.path.isfile(fname):
            raise Exception("File `%s` not found!" % fname)

        return os.path.abspath(fname)
