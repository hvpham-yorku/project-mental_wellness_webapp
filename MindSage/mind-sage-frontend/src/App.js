import React from "react";
import { Routes, Route } from "react-router-dom";
import './App.css';
import Home from "./pages/Home";
import JournalPage from "./pages/JournalPage";

function App() {
    return (
        <div className="App">
            <Routes>
                <Route path="/" element={<Home/>} />
                <Route path="/journal" element={<JournalPage/>} />
            </Routes>
        </div>
    );
}

export default App;
