import { useState, useEffect, useContext, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Webcam from "react-webcam";

import { InputField } from "@/components/forms/InputField";
import { PrimaryButton } from "@/components/buttons/PrimaryButton";
import { FormMessage } from "@/components/forms/FormMessage";
import { AuthContext } from "@/context/AuthContext";

export const Signin = () => {
  const [email, setEmail] = useState("");
  const [isFaceAuthEnabled, setIsFaceAuthEnabled] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [password, setPassword] = useState("");
  const [showTraditionalSignin, setShowTraditionalSignin] = useState(false);
  
  // Refs, hooks, and context
  const navigate = useNavigate();
  const location = useLocation();
  const webcamRef = useRef(null);
  const { login, checkFaceAuth } = useContext(AuthContext);

  useEffect(() => {
    const checkAuthCookie = async () => {
      try {
        const response = await checkFaceAuth();
        
        if (response.can_use_face_auth) {
          setIsFaceAuthEnabled(true);
          if (response.email) {
            setEmail(response.email);
          }
        } else {
          setIsFaceAuthEnabled(false);
        }
      } catch (error) {
        console.error("Error checking face auth:", error);
        setIsFaceAuthEnabled(false);
      }
    };
    checkAuthCookie();

    if (location.state && location.state.email) {
      setEmail(location.state.email);
    }
  }, [location, checkFaceAuth]);

  // Authentication methods
  const authenticateWithFace = async () => {
    try {
      const formData = new FormData();
      const imageSrc = webcamRef.current.getScreenshot();
      formData.append("image", imageSrc);
      
      const result = await fetch("/signin_via_face", {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      
      const data = await result.json();
      
      if (data.success) {
        setMessage("Face authentication successful.");
        setMessageType("success");
        navigate("/me");
      } else {
        setMessage("Face authentication failed. Please try password login.");
        setMessageType("error");
      }
    } catch (error) {
      setMessage("Face authentication failed.");
      setMessageType("error");
      console.error(error);
    }
  };

  const submitLoginForm = async (e) => {
    e.preventDefault();

    try {
      const result = await login({ email, password });

      if (result && result.success) {
        setMessage("Login successful.");
        setMessageType("success");
        navigate("/me");
        
      } else {
        if (
          result.status === 403 &&
          result.message.includes("Email not verified")
        ) {
          setMessage(result.message);
          setMessageType("success");
        } else if (result.status === 401) {
          setMessage("Invalid username or password. Please try again.");
          setMessageType("error");
        } else {
          setMessage("Login failed. Please try again later.");
          setMessageType("error");
        }
      }
    } catch (error) {
      setMessage("Login failed due to a server error.");
      setMessageType("error");
      console.log(error);
    }
  };

  // Render methods
  const renderFaceAuth = () => (
    <div className="face-auth">
      <Webcam
        audio={false}
        ref={webcamRef}
        width={400}
        height={400}
        screenshotFormat="image/jpeg"
      />
      
      <div className="form__button-group">
        <PrimaryButton 
          type="button" 
          onClick={authenticateWithFace}
        >
          Authenticate with Face
        </PrimaryButton>
        
        <PrimaryButton 
          type="button" 
          onClick={() => setShowTraditionalSignin(true)}
          variant="secondary"
        >
          Use Password Instead
        </PrimaryButton>
      </div>
    </div>
  );

  const renderTraditionalSignin = () => (
    <form onSubmit={submitLoginForm}>
      <InputField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      
      <InputField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      
      <div className="form__button-group">
        {isFaceAuthEnabled && (
          <PrimaryButton 
            type="button" 
            onClick={() => setShowTraditionalSignin(false)}
            variant="secondary"
          >
            Use Face Authentication
          </PrimaryButton>
        )}
        
        <PrimaryButton 
          type="submit" 
          fullWidth
        >
          Signin
        </PrimaryButton>
      </div>
    </form>
  );
  
  // Main render
  return (
    <div className="form">
      <div className="form__box modal">
        <h2 className="form__title">Signin</h2>
        <FormMessage message={message} isError={messageType === "error"} />
        
        {isFaceAuthEnabled && !showTraditionalSignin && renderFaceAuth()}
        {(!isFaceAuthEnabled || showTraditionalSignin) && renderTraditionalSignin()}
      </div>
    </div>
  );
};
