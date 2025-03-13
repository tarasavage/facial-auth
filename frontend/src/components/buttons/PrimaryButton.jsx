import PropTypes from "prop-types";

export const PrimaryButton = ({ type, onClick, children, disabled }) => {
  return (
    <button
      type={type}
      className={`button button--primary ${disabled ? "button--disabled" : ""}`}
      onClick={onClick}
      disabled={disabled}
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
};

PrimaryButton.defaultProps = {
  type: "button",
  disabled: false,
};
