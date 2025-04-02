import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Journaling from "../components/Journaling";
import axios from "axios";
import "../home.css";

const JournalPage = () => {
    const [journalText, setJournalText] = useState("");
    const navigate = useNavigate(); 

    const handleSubmit = async () => {
        try {
            const token = localStorage.getItem("access_token"); 
    
            if (!token) {
                alert("You must be logged in to save a journal.");
                return;
            }
    
            const response = await axios.post(
                "http://localhost:5000/api/add-journal",
                { content: journalText },
                {
                    headers: {
                        "Authorization": `Bearer ${token}`,  
                        "Content-Type": "application/json"
                    }
                }
            );
    
            if (response.status === 201) {
                alert("Journal saved successfully!");
                setJournalText(""); // ✅ Clear input after saving
            } else {
                alert(`Error: ${response.data.error || "Failed to save journal."}`);
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
                <button onClick={handleSubmit}>Save Journal</button>
                <button onClick={() => navigate("/Home")} className="button">Go Home</button>
            </div>
        </div>
    );
};

export default JournalPage;
