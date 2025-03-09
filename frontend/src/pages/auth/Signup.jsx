import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { FormMessage } from "@/components/forms/FormMessage";
import { InputField } from "@/components/forms/InputField";
import { PrimaryButton } from "@/components/buttons/PrimaryButton";

export const Signup = () => {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch(`${backendUrl}/registration/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log(data);
        navigate("/confirm-signup", { state: { email } });
      } else {
        setError(data.message || "Registration failed. Please try again.");
      }
    } catch (err) {
      console.error("Signup error:", err);
      setError(
        err.message || "An error occurred during signup. Please try again.",
      );
    }
  };

  return (
    <div className="form">
      <div className="form__box modal">
        <h2 className="form__title">Sign Up</h2>
        <FormMessage message={error} isError={true} />

        <form onSubmit={handleSubmit}>
          <InputField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <InputField
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <InputField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <InputField
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <PrimaryButton type="submit" fullWidth>
            Sign Up
          </PrimaryButton>
        </form>
      </div>
    </div>
  );
};
