import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./Home";
import JournalPage from "./JournalPage";
import "../components/Journaling.css"; 

const App = () => {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/journal" element={<JournalPage />} />
        </Routes>
    );
};

export default App;
