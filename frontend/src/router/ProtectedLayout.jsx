import { Outlet } from 'react-router-dom';

export const ProtectedLayout = () => {
    return (
        <div className="protected-layout">
            <div className="protected-layout__content">
                <Outlet />
            </div>
        </div>
    )
};