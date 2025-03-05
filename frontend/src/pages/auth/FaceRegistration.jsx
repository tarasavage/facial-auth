import { useState, useRef, useCallback } from "react";
import Webcam from "react-webcam";

export const FaceRegistration = () => {
    const webcamRef = useRef(null);
    const [image, setImage] = useState(null)


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
            formData.append('image', blob);
            // TODO: get api from env
            const api = 'http://0.0.0.0:8000';
            const uploadResponse = await fetch(`${api}/registration/register_user_face`, {
                method: "POST",
                headers: {
                    // TODO: get access token from local storage
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                },
                body: formData,
            });
            const data = await uploadResponse.json();
            console.log(data);
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
