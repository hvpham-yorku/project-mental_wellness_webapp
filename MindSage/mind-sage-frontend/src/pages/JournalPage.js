import React, { useState } from "react";
import Journalling from "../components/Journaling.js";

const JournalPage = () => {
    const [journalText, setJournalText] = useState("");
    
    return (
        <div className="journal-page">
            <h2>My Journal</h2>
            <p>Write your thoughts below and analyze your mood patterns or save your entry.</p>
            
            
            <Journalling 
                journalText={journalText} 
                setJournalText={setJournalText} 
            />
            
            
        </div>
    );
};

export default JournalPage;