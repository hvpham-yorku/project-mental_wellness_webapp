// src/App.js
import React from "react";
import { Routes, Route } from "react-router-dom";
import './App.css';
import Home from "./pages/Home";
import JournalPage from "./pages/JournalPage";
import Login from "./pages/login";
import SignUp from "./pages/SignUp";  // Import SignUp component

function App() {
    return (
        <div className="App">
            <Routes>
                <Route path="/" element={<Login />} />  {/* Default login route */}
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<SignUp />} />  {/* Add signup route */}
                <Route path="/home" element={<Home />} />
                <Route path="/journal" element={<JournalPage />} />
            </Routes>
        </div>
    );
}

export default App;
