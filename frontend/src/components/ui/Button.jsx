/**
 * A standardized button
 */
const Button = ({ children, onClick, type = 'button', variant = 'primary', disabled = false }) => {
  const baseStyle = "w-full py-2 px-4 rounded-md font-semibold text-white transition-all duration-200 shadow-sm";
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50",
    danger: "bg-red-600 hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-opacity-50",
  };
  const disabledStyle = "bg-gray-400 cursor-not-allowed";

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${disabled ? disabledStyle : variants[variant]}`}
    >
      {disabled ? 'Loading...' : children}
    </button>
  );
};

export default Button;
