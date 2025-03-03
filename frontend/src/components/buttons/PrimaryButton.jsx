export const PrimaryButton = ({ type, onClick, children, disabled }) => {
    return (
      <button 
        type={type} 
        className={`button button--primary ${disabled ? 'button--disabled' : ''}`} 
        onClick={onClick} 
        disabled={disabled}>
        {children}
      </button>
    );
  };
  
  export default PrimaryButton;