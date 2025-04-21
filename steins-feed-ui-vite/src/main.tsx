import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from "react-router"

import App from '@/App'
import LoginPage from "@/pages/login"

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={ <App /> } />
        <Route path="/login/" element={ <LoginPage /> } />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
