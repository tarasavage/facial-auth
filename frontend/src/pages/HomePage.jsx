import { Header } from "@/components/layout/Header";

export const HomePage = () => {
  return (
    <div className="home">
      <Header />
      <div className="home__container">
        <div className="home__content">
          <h1>Welcome to FaceAuth</h1>
          <p>Secure authentication using facial recognition</p>
        </div>
      </div>
    </div>
  );
};
