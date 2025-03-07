import { useState, useEffect, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { InputField } from '@/components/forms/InputField';
import { PrimaryButton } from '@/components/buttons/PrimaryButton';
import { FormMessage } from '@/components/forms/FormMessage';
import { AuthContext } from '@/context/AuthContext';

export const Signin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('');
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useContext(AuthContext);

    useEffect(() => {
        if (location.state && location.state.email) {
            setEmail(location.state.email);
        }
    }, [location]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const result = await login({ email, password });
      
            if (result && result.success) {
              setMessage('Login successful.');
              setMessageType('success');
              setTimeout(() => {
                navigate('/me');
              }, 3000); // Show the success message for 3 seconds before redirecting
            } else {
              if (result.status === 403 && result.message.includes("Email not verified")) {
                setMessage(result.message);
                setMessageType('success');
              } else if (result.status === 401) {
                setMessage('Invalid username or password. Please try again.');
                setMessageType('error');
              } else {
                setMessage('Login failed. Please try again later.');
                setMessageType('error');
              }
            }
          } catch (error) {
            setMessage('Login failed due to a server error.');
            setMessageType('error');
            console.log(error);
          }
    }


    return (
        <div className="form">
            <div className="form__box modal">
                <h2 className="form__title">Signin</h2>
                <FormMessage message={message} isError={messageType === 'error'} />
                <form onSubmit={handleSubmit}>
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
                        <PrimaryButton type="submit" fullWidth>Signin</PrimaryButton>
                    </div>
                </form>
            </div>
        </div>
    )
}