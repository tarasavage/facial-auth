import { Link } from "react-router-dom";
import { PrimaryButton } from "@/components/buttons/PrimaryButton";

import "@/styles/components/_header.scss";

export const Header = () => {
  return (
    <header className="header">
      <div className="header__content">
        <Link to="/" className="header__logo">
          FaceAuth
        </Link>
        <nav className="header__nav">
          <Link to="/signin" className="header__link">
            <PrimaryButton variant="secondary">Sign In</PrimaryButton>
          </Link>
          <Link to="/signup" className="header__link">
            <PrimaryButton>Sign Up</PrimaryButton>
          </Link>
        </nav>
      </div>
    </header>
  );
}; 