import { useState, useRef, useCallback } from "react";
import Webcam from "react-webcam";

export const FaceRegistration = () => {
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  const webcamRef = useRef(null);
  const [image, setImage] = useState(null);
  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
  }, [webcamRef]);

  const retake = () => {
    setImage(null);
  };

  const registerFace = async () => {
    try {
      const response = await fetch(image);
      const blob = await response.blob();
      const formData = new FormData();
      formData.append("image", blob);
      await fetch(
        `${backendUrl}/registration/register_user_face`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: formData,
        },
      );
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <div className="flex flex-col items-center justify-center">
        <Webcam
          audio={false}
          ref={webcamRef}
          width={400}
          height={400}
          screenshotFormat="image/jpeg"
        />
      </div>
      <div className="flex flex-col items-center justify-center">
        <button onClick={capture}>Capture</button>
        <button onClick={retake}>Retake</button>
        <button onClick={registerFace}>Register</button>
      </div>
    </div>
  );
};
