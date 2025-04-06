import { useState, useEffect, useContext } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { InputField } from "@/components/forms/InputField";
import { PrimaryButton } from "@/components/buttons/PrimaryButton";
import { FormMessage } from "@/components/forms/FormMessage";
import { AuthContext } from "@/context/AuthContext";

export const ConfirmSignup = () => {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const location = useLocation();
  const navigate = useNavigate();
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  const { userInfo } = useContext(AuthContext);

  useEffect(() => {
    // Redirect to profile if user is already logged in
    if (userInfo) {
      navigate("/me");
      return;
    }
    
    if (location.state && location.state.email) {
      setEmail(location.state.email);
    }
  }, [location, userInfo, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(
        `${backendUrl}/registration/confirm_signup`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, code }),
        },
      );
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || "Failed to confirm signup");
      } else {
        navigate("/signin", { state: { email } });
      }
    } catch (error) {
      const message =
        error || "An error occurred during signup. Please try again.";
      setError(message);
    }
  };

  return (
    <div className="form">
      <div className="form__box modal">
        <h2 className="form__title">Confirm Signup</h2>
        <FormMessage message={error} isError={true} />
        <form onSubmit={handleSubmit}>
          <InputField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={!!location.state?.email}
          />
          <InputField
            label="Confirmation Code"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            pattern="[0-9]*"
            inputMode="numeric"
          />
          <div className="form__button-group">
            <PrimaryButton type="submit" fullWidth>
              Confirm
            </PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  );
};
