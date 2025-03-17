import React, { useState } from "react";

const Login = () => {
  // This saves the email and password the user types
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // This function runs when the user clicks the Login button
  const handleLogin = async (event) => {
    event.preventDefault(); // Stops the page from refreshing

    setError(""); // Clear previous errors

    try {
      // Send email & password to backend
      const response = await fetch("http://127.0.0.1:8000/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json(); // Get the response from backend

      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }

      // Save the token in the browser
      localStorage.setItem("token", data.access_token);

      alert("Login successful!"); // Show a success message

      // Go to another page after login (example: dashboard)
      window.location.href = "/dashboard";

    } catch (err) {
      setError(err.message); // Show error if login fails
    }
  };

  return (
    <div>
      <h2>Login Page</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleLogin}>
        <div>
          <label>Email:</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <label>Password:</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
