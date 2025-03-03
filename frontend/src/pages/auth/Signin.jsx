import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { InputField } from '@/components/forms/InputField';
import { PrimaryButton } from '@/components/buttons/PrimaryButton';
import { FormMessage } from '@/components/forms/FormMessage';

export const Signin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();
    useEffect(() => {
        if (location.state && location.state.email) {
            setEmail(location.state.email);
        }
    }, [location]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const apiUrl = 'http://0.0.0.0:8000';

        try {
            const response = await fetch(`${apiUrl}/registration/signin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            if (response.status === 200) {
                navigate('/', { state: { email } });
            } else {
                setError(data.detail[0].msg || 'Failed to signin');
                return;
            }
        } catch (error) {
            const message = error || "An error occurred during signin. Please try again.";
            setError(message);
        }
    }


    return (
        <div className="form">
            <div className="form__box modal">
                <h2 className="form__title">Signin</h2>
                <FormMessage message={error} isError={true} />
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