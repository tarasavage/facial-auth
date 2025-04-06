import { useContext, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "@/context/AuthContext";
import { PrimaryButton } from "@/components/buttons/PrimaryButton";
import { FormMessage } from "@/components/forms/FormMessage";

export const ProfilePage = () => {
  const { userInfo, logout, checkFaceAuth } = useContext(AuthContext);
  const [faceAuthStatus, setFaceAuthStatus] = useState(null);
  const [message] = useState("");
  const [messageType] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const checkFaceAuthStatus = async () => {
      try {
        const response = await checkFaceAuth();
        setFaceAuthStatus(response.can_use_face_auth);
      } catch (error) {
        console.error("Error checking face auth status:", error);
        setFaceAuthStatus(false);
      }
    };

    checkFaceAuthStatus();
  }, [checkFaceAuth]);

  const handleLogout = () => {
    setIsLoading(true);
    logout();
  };

  if (!userInfo) {
    return (
      <div className="profile">
        <div className="profile__container">
          <h1>Loading user information...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="profile__container">
        <div className="profile__header">
          <h1>User Profile</h1>
          <PrimaryButton 
            onClick={handleLogout} 
            variant="danger"
            isLoading={isLoading}
            className="profile__logout-btn"
          >
            Logout
          </PrimaryButton>
        </div>

        <FormMessage message={message} isError={messageType === "error"} />

        <div className="profile__card">
          <div className="profile__info">
            <div className="profile__field">
              <strong>Username:</strong>
              <span>{userInfo.username}</span>
            </div>
            <div className="profile__field">
              <strong>Email:</strong>
              <span>{userInfo.email}</span>
            </div>
            <div className="profile__field">
              <strong>Email Verified:</strong>
              <span>{userInfo.email_verified ? "Yes" : "No"}</span>
            </div>
            <div className="profile__field">
              <strong>Face Authentication:</strong>
              <span>{faceAuthStatus ? "Enabled" : "Not Enabled"}</span>
            </div>
          </div>

          <div className="profile__actions">
            {!faceAuthStatus && (
              <Link to="/register-face">
                <PrimaryButton>Setup Face Authentication</PrimaryButton>
              </Link>
            )}
            {faceAuthStatus && (
              <Link to="/register-face">
                <PrimaryButton>Update Face Authentication</PrimaryButton>
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
