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
  const [isLoading, setIsLoading] = useState(false);
  
  // Refs, hooks, and context
  const navigate = useNavigate();
  const location = useLocation();
  const webcamRef = useRef(null);
  const { login, checkFaceAuth, refreshToken } = useContext(AuthContext);

  const backendUrl = import.meta.env.VITE_BACKEND_URL;

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
    if (!webcamRef.current) {
      setMessage("Camera not initialized. Please refresh the page.");
      setMessageType("error");
      return;
    }
    
    try {
      setIsLoading(true);
      setMessage("Processing your face authentication...");
      setMessageType("info");
      
      const formData = new FormData();
      const imageSrc = await fetch(webcamRef.current.getScreenshot());
      const blob = await imageSrc.blob();
      formData.append("image", blob);
      
      const result = await fetch(
        `${backendUrl}/registration/signin_via_face`,
        {
          method: "POST",
          credentials: "include",
          body: formData,
        },
      );
      
      const data = await result.json();
      
      if (data.success) {
        if (!data.access_token) { 
          setMessage("Face authentication failed. Please try password login.");
          setMessageType("error");
          return;
        }
        
        refreshToken(data.access_token);
        
        setMessage("Face authentication successful.");
        setMessageType("success");
        
        setTimeout(() => {
          navigate("/me");
        }, 500);
      } else {
        setMessage("Face authentication failed. Please try password login.");
        setMessageType("error");
      }
    } catch (error) {
      setMessage("Face authentication failed.");
      setMessageType("error");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const submitLoginForm = async (e) => {
    e.preventDefault();
    setIsLoading(true);

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
    } finally {
      setIsLoading(false);
    }
  };

  // Render methods
  const renderFaceAuth = () => (
    <div className="face-auth">
      <div className="face-auth__webcam">
        <Webcam
          audio={false}
          ref={webcamRef}
          width={320}
          height={320}
          screenshotFormat="image/jpeg"
          videoConstraints={{
            facingMode: "user",
            width: 320,
            height: 320
          }}
        />
      </div>
      
      <div className="form__button-group">
        <PrimaryButton 
          type="button" 
          onClick={authenticateWithFace}
          disabled={isLoading}
        >
          {isLoading ? "Authenticating..." : "Authenticate with Face"}
        </PrimaryButton>
        
        <PrimaryButton 
          type="button" 
          onClick={() => setShowTraditionalSignin(true)}
          variant="secondary"
          disabled={isLoading}
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
        id="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      
      <InputField
        label="Password"
        type="password"
        id="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      
      <div className="form__button-group">
        {isFaceAuthEnabled && (
          <PrimaryButton 
            type="button" 
            onClick={() => setShowTraditionalSignin(false)}
            variant="secondary"
            disabled={isLoading}
          >
            Use Face Authentication
          </PrimaryButton>
        )}
        
        <PrimaryButton 
          type="submit" 
          disabled={isLoading}
          isLoading={isLoading}
          className="signin-button"
        >
          Sign In
        </PrimaryButton>
      </div>
    </form>
  );
  
  // Main render
  return (
    <div className="signin-page">
      <div className="form">
        <div className="form__box modal">
          <h2 className="form__title">Sign In</h2>
          <FormMessage message={message} isError={messageType === "error"} />
          
          {isFaceAuthEnabled && !showTraditionalSignin && renderFaceAuth()}
          {(!isFaceAuthEnabled || showTraditionalSignin) && renderTraditionalSignin()}
          
          <div className="signup-link">
            <p>Don&apos;t have an account?</p>
            <PrimaryButton 
              type="button"
              variant="secondary"
              onClick={() => navigate("/signup")}
              className="signup-button"
            >
              Sign Up
            </PrimaryButton>
          </div>
        </div>
      </div>
    </div>
  );
};
