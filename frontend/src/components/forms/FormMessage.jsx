export const FormMessage = ({ message, isError }) => {
    if (!message) return null;
  
    const messageClass = isError ? 'message--error' : 'message--success';
  
    return (
      <div className={`message-container`}>
        <div className={`message ${messageClass}`} style={{ color: isError ? 'red' : 'black' }}>
          {message}
        </div>
      </div>
    );
  };
  