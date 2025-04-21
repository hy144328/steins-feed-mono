import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from "react-router"

import HomePage from '@/pages/home'
import LoginPage from "@/pages/login"

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={ <HomePage /> } />
        <Route path="/login/" element={ <LoginPage /> } />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
