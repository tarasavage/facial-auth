import PropTypes from "prop-types";

export const InputField = ({ label, type, id, value, onChange, disabled }) => (
  <div className="form__group">
    <label htmlFor={id} className="form__label">
      {label}:
    </label>
    <input
      type={type}
      id={id}
      value={value}
      onChange={onChange}
      required
      disabled={disabled}
      className={`form__input ${disabled ? "form__input--disabled" : ""}`}
    />
  </div>
);

InputField.propTypes = {
  label: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

InputField.defaultProps = {
  disabled: false,
};
