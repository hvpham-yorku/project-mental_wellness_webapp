import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import "../home.css";

const EmojiSlider = ({ value, onChange, emojis }) => {

    return (
        <div style={{ display: "flex", alignItems: "center" }}>
            <span>{emojis[0]}</span>
            <Slider
                min={0}
                max={100}
                value={value}
                onChange={onChange}
                trackStyle={{ backgroundColor: "#4caf50" }}
                handleStyle={{ borderColor: "#4caf50", height: 20, width: 20 }}
                railStyle={{ backgroundColor: "#ddd" }}
            />
            <span>{emojis[emojis.length - 1]}</span>
        </div>
    );
};

function Home() {
    const navigate = useNavigate(); //hook for buttons that navigate pages

    const [moodData, setMoodData] = useState({
        happiness: 50,
        anxiety: 50,
        energy: 50,
        stress: 50,
        activity: "",
        notes: "",
    });

    const [message, setMessage] = useState("");
    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Submit button clicked!");
    
        const token = localStorage.getItem("access_token");
        if (!token) {
            setMessage("You must be logged in to add a mood entry.");
            console.log("No token found, user not logged in.");
            return;
        }
    
        console.log("Sending data:", moodData);
    
        try {
            const response = await axios.post(
                "http://localhost:5000/api/add-mood-entry",
                moodData,
                {
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    }
                }
            );
    
            console.log("Full Response:", response);
            console.log("Response Data:", response.data);
    
            if (response.data.success) {
                setMessage("Mood entry added successfully!");
                console.log("Mood entry added:", response.data.data);
    
                setTimeout(() => {
                    setMoodData({
                        happiness: 50,
                        anxiety: 50,
                        energy: 50,
                        stress: 50,
                        activity: "",
                        notes: ""
                    });
                }, 500); 
            } else {
                setMessage(`Error: ${response.data.error || "Failed to add entry."}`);
            }
    
        } catch (error) {
            console.error("Error adding mood entry:", error.response?.data || error);
            setMessage("An error occurred while adding the mood entry.");
        }
    };

    return (
        <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
            <h1>MindSage Mood Tracker</h1>
            <form onSubmit={handleSubmit}>
                {message && (
                    <p style={{
                        color: message.includes("successfully") ? "green" : "red",
                        fontWeight: "bold",
                        textAlign: "center"
                        }}>
                            {message}
                        </p>
                    )}  
                <div style={{ marginBottom: "20px" }}>
                    <label>Happiness:</label>
                    <EmojiSlider
                        value={moodData.happiness}
                        onChange={(value) => setMoodData({ ...moodData, happiness: value })}
                        emojis={["😢", "😐", "😊"]}
                    />
                </div>
                <div style={{ marginBottom: "20px" }}>
                    <label>Anxiety:</label>
                    <EmojiSlider
                        value={moodData.anxiety}
                        onChange={(value) => setMoodData({ ...moodData, anxiety: value })}
                        emojis={["😌", "😐", "😰"]}
                    />
                </div>
                <div style={{ marginBottom: "20px" }}>
                    <label>Energy:</label>
                    <EmojiSlider
                        value={moodData.energy}
                        onChange={(value) => setMoodData({ ...moodData, energy: value })}
                        emojis={["😴", "😐", "⚡️"]}
                    />
                </div>
                <div style={{ marginBottom: "20px" }}>
                    <label>Stress:</label>
                    <EmojiSlider
                        value={moodData.stress}
                        onChange={(value) => setMoodData({ ...moodData, stress: value })}
                        emojis={["😎", "😐", "🤯"]}
                    />
                </div>
                <div style={{ marginBottom: "10px" }}>
                    <label>Activity:</label>
                    <input
                        type="text"
                        value={moodData.activity}
                        onChange={(e) => setMoodData({ ...moodData, activity: e.target.value })}
                    />
                </div>
                <div style={{ marginBottom: "10px" }}>
                    <label>Notes:</label>
                    <textarea
                        value={moodData.notes}
                        onChange={(e) => setMoodData({ ...moodData, notes: e.target.value })}
                    />
                </div>
                <button type="submit">Submit Mood Entry</button>
            </form>
            <div>
                <button onClick={() => navigate("/journal")} className="button">Go to Journal</button>
            </div>
        </div>

    );
}

export default Home;
