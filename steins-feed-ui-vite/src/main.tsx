import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from "react-router"

import FeedPage from "@/pages/feed"
import HomePage from '@/pages/home'
import LoginPage from "@/pages/login"

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={ <HomePage /> } />
        <Route path="/login/" element={ <LoginPage /> } />
        <Route path="/feed/:feed_id/" element={ <FeedPage /> } />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
