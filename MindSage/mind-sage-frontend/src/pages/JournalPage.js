import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Journaling from "../components/Journaling";
import axios from "axios";

const JournalPage = () => {
    const [journalText, setJournalText] = useState("");
    const navigate = useNavigate(); 

    const handleSubmit = async () => {
        try {
            const response = await axios.post("http://localhost:5000/api/add-journal", {
                content: journalText,
            });

            if (response.status === 201) {
                alert("Journal saved successfully!");
                setJournalText(""); // Clear the text area after submission
            }
        } catch (error) {
            console.error("Error saving journal:", error);
            alert("Failed to save the journal. Please try again.");
        }
    };

    return (
        <div>
            <div>
                <h1>Dear Journal...</h1>
                <Journaling journalText={journalText} setJournalText={setJournalText} />
            </div>
            <div>
                <button onClick={() => navigate("/")}>Go Home</button>
                <button onClick={handleSubmit}>Save Journal</button>
            </div>
        </div>
    );
};

export default JournalPage;
