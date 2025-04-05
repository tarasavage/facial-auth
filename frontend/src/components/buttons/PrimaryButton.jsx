import PropTypes from "prop-types";

export const PrimaryButton = ({ 
  type, 
  onClick, 
  children, 
  disabled, 
  variant = "primary", 
  fullWidth, 
  isLoading,
  className
}) => {
  const buttonClass = `button button--${variant} ${fullWidth ? 'button--full' : ''} ${isLoading ? 'button--loading' : ''} ${className || ''}`;
  
  return (
    <button
      type={type}
      className={buttonClass}
      onClick={onClick}
      disabled={disabled || isLoading}
    >
      {children}
    </button>
  );
};

PrimaryButton.propTypes = {
  type: PropTypes.string,
  onClick: PropTypes.func,
  children: PropTypes.node.isRequired,
  disabled: PropTypes.bool,
  variant: PropTypes.oneOf(["primary", "secondary", "danger", "google", "apple", "icon"]),
  fullWidth: PropTypes.bool,
  isLoading: PropTypes.bool,
  className: PropTypes.string
};

PrimaryButton.defaultProps = {
  type: "button",
  disabled: false,
  variant: "primary",
  fullWidth: false,
  isLoading: false,
  className: ''
};
