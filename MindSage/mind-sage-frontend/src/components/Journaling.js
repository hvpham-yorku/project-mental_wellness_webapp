import React from "react";
import "./Journaling.css"; // Create this file for styling

const Journalling = ({ journalText, setJournalText}) => {
    return (
        <textarea
            className="paper"
            placeholder="Start writing here..."
            value={journalText}
            onChange={(e) => setJournalText(e.target.value)}
        ></textarea>
    );
};

export default Journalling;
