/**
 * An error message component
 */
const ErrorMessage = ({ message }) => {
  if (!message) return null;
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-md my-2 text-sm">
      {message}
    </div>
  );
};

export default ErrorMessage;
