import React from "react";
import { useNavigate } from "react-router-dom";
import Journaling from "../components/Journaling";

const JournalPage = () => {
    const navigate = useNavigate(); 

    return (
        <div>
            <div>
                <h1>Dear Journal...</h1>
                <Journaling />
            </div>
            <div>
                <button onClick={() => navigate("/")}>Go Home</button>
            </div>
        </div>
    );
};

export default JournalPage;
