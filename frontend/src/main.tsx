import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { APP_COPY, DOM_ID } from './constants/app'

const rootElement = document.getElementById(DOM_ID.ROOT)

if (!rootElement) {
  throw new Error(APP_COPY.ROOT_ELEMENT_NOT_FOUND)
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
