import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ChatProvider } from './context/ChatContext.tsx'
import { AuthProvider, useAuth } from './context/AuthContext.tsx'
import LoginPage from './components/LoginPage.tsx'

function RootApp() {
  const { token } = useAuth()
  
  if (!token) {
    return <LoginPage />
  }

  return (
    <ChatProvider>
      <App />
    </ChatProvider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RootApp />
    </AuthProvider>
  </StrictMode>,
)
