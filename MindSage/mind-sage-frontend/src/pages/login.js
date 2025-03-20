import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import axios from "axios";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isSignup, setIsSignup] = useState(false); // Toggle between signup and login
  const [error, setError] = useState("");
  const navigate = useNavigate(); // Initialize useNavigate

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post("http://localhost:5000/api/login", {
        email,
        password,
      });

      if (response.data.success) {
        setMessage("Login successful!");
        localStorage.setItem("access_token", response.data.access_token);
        navigate("/home"); // Redirect to home page
      } else {
        setMessage(`Login failed: ${response.data.message || "Unknown error"}`);
      }
    } catch (err) {
      console.error("Login Error:", err.response || err.message || err);
      setMessage("Error occurred during login. Please check the console for more details.");
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/api/signup", {
        email,
        password,
      });

      if (response.data.success) {
        setMessage("Account created successfully! Please log in.");
        setIsSignup(false); // Switch back to login after signup
      } else {
        setMessage(`Failed to create account: ${response.data.message || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Signup Error:", error.response || error.message || error);
      setMessage("Error occurred during signup. Please check the console for more details.");
    }
  };

  return (
    <div>
      <h1>{isSignup ? "Sign Up" : "Login"}</h1>
      <form onSubmit={isSignup ? handleSignup : handleLogin}>
        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">{isSignup ? "Sign Up" : "Login"}</button>
      </form>

      {message && <p>{message}</p>}

      <p>
        {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
        <a href="#" onClick={() => setIsSignup(!isSignup)}>
          {isSignup ? "Login here" : "Sign up here"}
        </a>
      </p>

      {error && <p>{error}</p>}
    </div>
  );
};

export default LoginPage;
