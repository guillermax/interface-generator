# Frontend - Interface Generator

React приложение для взаимодействия с системой генерации интерфейсов.

## 📦 Структура компонентов

### ChatInterface
Главный контейнер приложения, управляющий состоянием сообщений и выбранным сообщением.

**Props**: нет

**State**:
- `messages` - массив сообщений
- `selectedMessage` - выбранное сообщение для предпросмотра

### ChatHistory
Боковая панель с историей сообщений пользователя.

**Props**:
- `messages` - массив всех сообщений
- `selectedMessage` - текущее выбранное сообщение
- `onSelectMessage` - callback для выбора сообщения

**Features**:
- Кнопка "New Chat"
- Список сообщений с усечением текста
- Выделение выбранного сообщения

### ChatInput
Поле ввода сообщений с автоматическим расширением.

**Props**:
- `onSendMessage` - callback при отправке сообщения

**Features**:
- Автоматическое расширение textarea
- Отправка по Ctrl+Enter или кнопке
- Disabled состояние при загрузке

### PreviewPanel
Панель предпросмотра с двумя вкладками: Code и Preview.

**Props**:
- `message` - сообщение с preview данными

**Features**:
- Вкладка "Code" - просмотр HTML и CSS
- Вкладка "Preview" - живой iframe с результатом
- Кнопки копирования кода

## 🎨 Tailwind CSS

Проект использует утилиты Tailwind CSS для стилизации:
- `w-64` - ширина боковых панелей
- `flex` - флекс раскладка
- `bg-white`, `bg-gray-50` - цвета фона
- `border-` - границы
- `rounded-lg` - скругленные углы

Все стили написаны inline в компонентах.

## 🔄 Поток данных

```
ChatInterface (state)
├── ChatHistory (читает messages, selectedMessage)
├── ChatInput (отправляет новое сообщение)
└── PreviewPanel (отображает preview выбранного сообщения)
```

## 🚀 Развертывание

### Development
```bash
npm run dev
```

### Production
```bash
npm run build
npm run preview
```

Built files будут в `dist/` папке.

## 📝 Типы

```typescript
interface Message {
  id: string
  text: string
  role: 'user' | 'assistant'
  timestamp: Date
  preview?: {
    html: string
    css: string
  }
}
```
