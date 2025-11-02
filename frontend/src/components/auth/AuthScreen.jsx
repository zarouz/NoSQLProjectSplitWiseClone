import { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

/**
 * Login & Register Screen
 */
const AuthScreen = () => {
  const [isLogin, setIsLogin] = useState(true);
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        {isLogin ? <LoginForm /> : <RegisterForm />}
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="w-full text-center text-sm text-blue-600 hover:underline mt-4"
        >
          {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
        </button>
      </div>
    </div>
  );
};

export default AuthScreen;
