import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./pages/App";  // Ensure App.js is in pages folder
import "./index.css";  // Adjust path to index.css
import reportWebVitals from "./pages/reportWebVitals.js"; // Ensure file exists

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <BrowserRouter>
        <App />
    </BrowserRouter>
);

reportWebVitals();
