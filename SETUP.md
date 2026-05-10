# Инструкции по запуску проекта

## ⚠️ Важно!

Из-за проблем с OneDrive синхронизацией (блокирует удаление файлов npm), **рекомендуется работать из локальной папки**:

```
C:\interface-generator-local\frontend
```

В этой папке уже установлены все зависимости и проект готов к запуску!

## 🚀 Быстрый старт (Рекомендуемый способ)

### 1. Запуск dev сервера из локальной папки

```bash
cd C:\interface-generator-local\frontend
npm run dev
```

Приложение откроется на **http://localhost:5173**

### 2. Скопировать исходный код в основную папку (опционально)

Если хотите работать в папке на OneDrive:

```bash
# После внесения изменений в локальной папке
Copy-Item -Path C:\interface-generator-local\frontend\src -Destination c:\Users\guill\OneDrive\Desktop\interface-generator\frontend -Recurse -Force

# Затем коммитить в git
cd c:\Users\guill\OneDrive\Desktop\interface-generator
git add .
git commit -m "Update components"
```

## 📝 Структура (OneDrive папка)

```
c:\Users\guill\OneDrive\Desktop\interface-generator\
├── frontend/                    # Исходный код, конфиги
│   ├── src/
│   │   ├── components/         # React компоненты
│   │   ├── types.ts            # TypeScript типы
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json            # Зависимости
│   ├── tailwind.config.js
│   └── tsconfig.json
├── backend/                     # FastAPI (пока пусто)
├── .gitignore
└── README.md
```

## 🔧 Установка зависимостей (если начинаете с OneDrive)

```bash
cd c:\Users\guill\OneDrive\Desktop\interface-generator\frontend

# Очистить npm кэш если будут ошибки
npm cache clean --force

# Установить зависимости
npm install

# Если выдает ошибку EPERM - работайте из C:\interface-generator-local
```

## 🎨 Что реализовано

### ✅ Компоненты

- **ChatInterface** (`src/components/ChatInterface.tsx`)
  - Главный контейнер с управлением состоянием
  - Mock API для демонстрации

- **ChatHistory** (`src/components/ChatHistory.tsx`)
  - Боковая панель слева
  - История сообщений пользователя
  - Кнопка "New Chat"

- **ChatInput** (`src/components/ChatInput.tsx`)
  - Поле ввода с автоматическим расширением
  - Отправка по Ctrl+Enter или кнопке
  - Состояние загрузки

- **PreviewPanel** (`src/components/PreviewPanel.tsx`)
  - Панель справа с двумя вкладками
  - Code - просмотр HTML/CSS
  - Preview - живой iframe
  - Кнопки копирования кода

### 📦 Зависимости

- React 19.2.5
- TypeScript 6.0.2
- Vite 8.0.10
- Tailwind CSS 4.2.4
- PostCSS 8.4.47
- Autoprefixer 10.4.20
- ESLint + Prettier

## 🧪 Тестирование интерфейса

1. Введите текст в поле ввода
   ```
   Пример: "Create a login form with email and password fields"
   ```

2. Нажмите Send или Ctrl+Enter

3. Справа появится панель предпросмотра с:
   - HTML кодом формы
   - CSS стилями
   - Живым превью в iframe

4. Можно переключаться между вкладками Code/Preview

5. Скопировать код через кнопки Copy HTML/Copy CSS

## 🛠️ Команды

```bash
# Development server (горячая перезагрузка)
npm run dev

# Проверка типов + сборка для production
npm run build

# Превью production сборки
npm run preview

# Проверка кода ESLint
npm run lint
```

## 📁 Структура исходного кода

```
src/
├── components/
│   ├── ChatInterface.tsx    - Главный контейнер
│   ├── ChatHistory.tsx      - История сообщений
│   ├── ChatInput.tsx        - Поле ввода
│   └── PreviewPanel.tsx     - Панель предпросмотра
├── types.ts                 - TypeScript типы (Message, ChatState)
├── App.tsx                  - Root компонент
├── App.css                  - Стили приложения
├── index.css                - Tailwind CSS импорт
└── main.tsx                 - Entry point
```

## 🔌 Mock API

Текущая реализация возвращает жестко закодированную форму авторизации:

```javascript
// src/components/ChatInterface.tsx, ~46 строка
const assistantMessage: Message = {
  preview: {
    html: `<form>...`,
    css: `body { ... }`
  }
}
```

Позже будет заменена на реальный вызов FastAPI сервера.

## 📚 Дополнительные ресурсы

- [React документация](https://react.dev/)
- [Vite документация](https://vitejs.dev/)
- [Tailwind CSS документация](https://tailwindcss.com/)
- [TypeScript документация](https://www.typescriptlang.org/)

## ⚡ Советы по разработке

1. **Hot Module Replacement (HMR)** - изменения в коде отражаются мгновенно
2. **ESLint** - проверка кода: `npm run lint`
3. **Tailwind IntelliSense** - установите расширение VS Code для автодополнения классов
4. **DevTools** - используйте React DevTools браузера для отладки компонентов

## 🐛 Решение проблем

### npm install зависает или выдает EPERM

**Решение**: Работайте из локальной папки `C:\interface-generator-local\frontend`

### Приложение не отображается

1. Проверьте, работает ли dev сервер
2. Откройте http://localhost:5173 в браузере
3. Посмотрите консоль браузера (F12) на ошибки
4. Проверьте консоль терминала на ошибки сборки

### Стили Tailwind не применяются

1. Убедитесь что установлен tailwindcss: `npm list tailwindcss`
2. Проверьте импорт в `src/index.css`: `@import 'tailwindcss';`
3. Перезагрузите сервер: остановите и запустите `npm run dev` заново

---

**Готово к запуску!** 🚀

Начните с:
```bash
cd C:\interface-generator-local\frontend
npm run dev
```
