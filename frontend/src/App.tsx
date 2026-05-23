import './App.css'
import ChatInterface from './components/ChatInterface'

function App() {
  // w-full (не w-screen) — не выходит за пределы #root
  return (
    <div className="w-full h-full flex overflow-hidden">
      <ChatInterface />
    </div>
  )
}

export default App
