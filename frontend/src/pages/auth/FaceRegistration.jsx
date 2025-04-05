import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Webcam from "react-webcam";
import { PrimaryButton } from "@/components/buttons/PrimaryButton";
import { FormMessage } from "@/components/forms/FormMessage";

export const FaceRegistration = () => {
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  const webcamRef = useRef(null);
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
  }, [webcamRef]);

  const retake = () => {
    setImage(null);
    setMessage("");
  };

  const registerFace = async () => {
    if (!image) {
      setMessage("Please capture your face image first");
      setMessageType("error");
      return;
    }

    try {
      setIsLoading(true);
      const imageBlob = await fetch(image);
      const blob = await imageBlob.blob();
      const formData = new FormData();
      formData.append("image", blob);
      
      const response = await fetch(
        `${backendUrl}/registration/register_user_face`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          credentials: "include",
          body: formData,
        },
      );
      
      const data = await response.json();
      
      if (response.ok) {
        setMessage("Face registered successfully! You can now use face authentication to login.");
        setMessageType("success");
        // After 2 seconds, redirect to profile page
        setTimeout(() => {
          navigate("/me");
        }, 2000);
      } else {
        setMessage(data.message || "Failed to register face. Please try again.");
        setMessageType("error");
      }
    } catch (error) {
      console.error(error);
      setMessage("An error occurred. Please try again.");
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="face-auth">
      <h2 className="face-auth__title">Face Authentication Setup</h2>
      <p className="face-auth__instructions">
        Position your face in the center of the camera. Make sure your face is well-lit
        and clearly visible. Remove glasses, hats, or anything covering your face.
      </p>
      
      <FormMessage message={message} isError={messageType === "error"} />
      
      <div className="face-auth__container">
        {!image ? (
          <div className="face-auth__webcam">
            <Webcam
              audio={false}
              ref={webcamRef}
              width={400}
              height={400}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                facingMode: "user"
              }}
            />
          </div>
        ) : (
          <img 
            src={image} 
            alt="Captured face" 
            className="face-auth__preview" 
          />
        )}
        
        <div className="face-auth__actions">
          {!image ? (
            <PrimaryButton 
              onClick={capture} 
              disabled={isLoading}
            >
              Capture Photo
            </PrimaryButton>
          ) : (
            <>
              <PrimaryButton 
                onClick={retake} 
                variant="secondary" 
                disabled={isLoading}
              >
                Retake Photo
              </PrimaryButton>
              
              <PrimaryButton 
                onClick={registerFace} 
                disabled={isLoading}
                isLoading={isLoading}
              >
                Register Face
              </PrimaryButton>
            </>
          )}
        </div>
      </div>

      <PrimaryButton 
        onClick={() => navigate("/me")} 
        variant="secondary"
      >
        Back to Profile
      </PrimaryButton>
    </div>
  );
};
