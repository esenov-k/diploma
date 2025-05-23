# Улучшение терминала и интеграция его в *Windows*

- [Улучшение терминала и интеграция его в *Windows*](#улучшение-терминала-и-интеграция-его-в-windows)
  - [Назначение документа](#назначение-документа)
  - [Установка **fish** и **tide**](#установка-fish-и-tide)
  - [Добавление **fish** в контекстное меню *Windows*](#добавление-fish-в-контекстное-меню-windows)
  - [Вызов **fish** сочетанием клавиш](#вызов-fish-сочетанием-клавиш)
  - [Добавление **fish** в *VS Code*](#добавление-fish-в-vs-code)


## Назначение документа

В настоящем файле написаны шаги, которые рекомендуется выполнить для упрощения
использования эмулятора терминала **Cygwin** и включают установку эмулятора
терминала **fish** с темой **tide** и интеграцию **Cygwin** в *Windows*.

## Установка **fish** и **tide**

1. Установить шрифты **Hack**, найти которые можно скачать по
          [ссылке](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/Hack.zip)
2. Установить **fish** и запустить его командой 
    ```
    apt-cyg install fish
    fish
    ```
3. Установить [**fisher**](https://github.com/jorgebucaran/fisher) с помощью команды 
    ```
    curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
    ```
4. В настройках терминала (ПКМ по верху окна) в группе *Text* выбрать
		шрифт *Hack Nerd Font Mono*;
5. Запустить установку темы [**tide**](https://github.com/IlanCosman/tide) с помощью команды
   ```
    fisher install IlanCosman/tide@v6
   ```
   и выбрать понравившиеся визуальные настройки;
6. Установить **fish** запускаемой по умолчанию командной строкой, для этого:
	- в терминале выполнить команды 
	  ```
      mkpasswd > /etc/passwd
      nano /etc/passwd
	  ```
	- переместить каретку с помощью стрелок до строки `user_name:*:....
	:/home/user_name:/bin/bash` и заменить `/bin/bash` на `/bin/fish` 
	- сохранить файл сочетанием клавиш <kbd>CTRL</kbd> + <kbd>O</kbd> и
	нажать <kbd>ENTER</kbd> 
	- выйти из редактора сочетанием клавиш <kbd>CTRL</kbd> + <kbd>X</kbd>

## Добавление **fish** в контекстное меню *Windows*

Добавление возможности открытия терминала в текущей папке с помощью
контекстного меню *Windows*, для этого необходимо: 
- выполнить команду 
  ```
  apt-cyg install chere
  ```
- запустить **Cygwin** с правами администратора
- выполнить команду: 
   ```
   chere -i -t mintty -s fish
   ```
    > Если нужно добавить запуск **bash**, то вместо **fish** написать
    > **bash**.
	
В контекстном меню в проводнике появится пункт **Fish Prompt Here**

> На некоторых машинах эта функция некорректно работает при попытке открыть
> терминал в сетевой папке.

## Вызов **fish** сочетанием клавиш

Для добавления возможности вызова **fish** сочетанием клавиш необходимо:
- нажать ПКМ по иконке **Cygwin** в меню пуск;
- нажать расположение файла;
- ПКМ по иконке и перейти в свойства;
- в поле быстрый вызов указать сочетание клавиш <kbd>CTRL</kbd> +
    <kbd>ALT</kbd> + <kbd>T</kbd>;
    > Можно установить и другое сочетание клавиш, но написанное выше
    > является стандартным для *Linux* систем.

## Добавление **fish** в *VS Code*

Чтобы иметь возможность открыть **fish** как терминал в *VS Code* необходимо в
файле настроек *settings.json* добавить следующие строки:

```    
  "terminal.integrated.profiles.windows": {
    "Cygwin for Windows": {
    "path": "C:\\cygwin64\\bin\\bash.exe",
    "args": ["--login","-lic", "fish"],
    "env": {"CHERE_INVOKING": "1"}
    }
  },

  "terminal.integrated.fontFamily": "Hack Nerd Font ",
  "terminal.integrated.defaultProfile.windows": "Cygwin for Windows"
```
   > Если установка проводилась не в директорию по умолчанию, то в параметре 
   >`"path"` необходимо указать актуальный путь установки.

После этого **fish** появится в списке возможных к запуску терминалов и будет
терминалом по умолчанию.