import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import Input from '../ui/Input';
import Button from '../ui/Button';
import ErrorMessage from '../ui/ErrorMessage';
import Spinner from '../ui/Spinner';

/**
 * Register Form Component
 */
const RegisterForm = () => {
  const { login, register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    // Frontend Password Validation (matches backend)
    if (password.length < 8 || !/[a-z]/.test(password) || !/[A-Z]/.test(password) || !/\d/.test(password)) {
      setError("Password must be 8+ chars, with upper, lower, and number.");
      setLoading(false);
      return;
    }

    const result = await register(name, email, password);
    setLoading(false);
    if (result.success) {
      setSuccess(true);
      // Automatically log in the user after successful registration
      await login(email, password);
    } else {
      setError(result.error);
    }
  };

  if (success) {
    return (
      <div className="text-center p-4">
        <h3 className="text-lg font-semibold text-green-600">Registration Successful!</h3>
        <p className="text-gray-700">Logging you in...</p>
        <Spinner />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <ErrorMessage message={error} />
      <Input label="Name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Alice Kumar" />
      <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="alice@vit.edu" />
      <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Must be 8+ chars, with upper, lower, & number" />
      <Button type="submit" disabled={loading}>Register</Button>
    </form>
  );
};

export default RegisterForm;
