import { useState, useEffect, useMemo } from 'react';
import { api } from '../api/api';
import { useAuth } from '../context/AuthContext';
import Spinner from '../components/ui/Spinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import Modal from '../components/ui/Modal';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

/**
 * Component for a single expense item
 */
const ExpenseItem = ({ expense, onExpenseDeleted }) => {
  const { user } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);

  // Check if the current user is the payer
  const isPayer = expense.paidBy?.id === user.id;

  const handleDelete = async () => {
    // Note: window.confirm is used here as a simple confirmation
    if (!window.confirm("Are you sure you want to delete this expense?")) return;
    setIsDeleting(true);
    try {
      await api.delete(`/expenses/${expense.id}`);
      onExpenseDeleted(expense.id);
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
      <div className="flex items-center space-x-4">
        <div className="text-center">
          <p className="text-xs text-gray-500">{new Date(expense.createdAt).toLocaleDateString('en-US', { month: 'short' })}</p>
          <p className="text-lg font-semibold text-gray-800">{new Date(expense.createdAt).getDate()}</p>
        </div>
        <div>
          <h4 className="font-semibold text-gray-800">{expense.description}</h4>
          <p className="text-sm text-gray-500">
            {expense.paidBy.name} paid <span className="font-bold text-gray-700">₹{expense.amount.toFixed(2)}</span>
          </p>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <p className="text-sm text-gray-600">
          {isPayer ? `You paid` : `You owe ₹${(expense.amount / expense.participants.length).toFixed(2)}`}
        </p>
        {isPayer && (
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-red-500 hover:text-red-700 p-2 rounded-full disabled:text-gray-400"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Modal to add a new expense
 */
const AddExpenseModal = ({ show, onClose, groupId, members, onExpenseAdded }) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // By default, select all members when modal opens
    if (members) {
      setSelectedMembers(members.map(m => m.id));
    }
  }, [members, show]);

  const handleMemberToggle = (memberId) => {
    setSelectedMembers(prev =>
      prev.includes(memberId)
        ? prev.filter(id => id !== memberId)
        : [...prev, memberId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedMembers.length === 0) {
      setError("You must select at least one participant.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.post('/expenses', {
        description,
        amount: parseFloat(amount),
        groupId,
        participantIds: selectedMembers,
      });
      onExpenseAdded(); // Notify parent to refetch
      onClose(); // Close modal
      // Reset form
      setDescription('');
      setAmount('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Add New Expense">
      <form onSubmit={handleSubmit} className="space-y-4">
        <ErrorMessage message={error} />
        <Input
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g., Hotel Booking"
        />
        <Input
          label="Amount (₹)"
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="e.g., 9000"
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Split with:</label>
          <div className="space-y-2 max-h-40 overflow-y-auto p-2 border rounded-md">
            {members.map(member => (
              <label key={member.id} className="flex items-center space-x-2 p-2 rounded-md hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={selectedMembers.includes(member.id)}
                  onChange={() => handleMemberToggle(member.id)}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">{member.name}</span>
              </label>
            ))}
          </div>
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Expense'}
        </Button>
      </form>
    </Modal>
  );
};

/**
 * Modal to add a new member
 */
const AddMemberModal = ({ show, onClose, groupId, onMemberAdded }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await api.post(`/groups/${groupId}/members`, { email });
      setSuccess(true);
      setEmail('');
      onMemberAdded(); // Notify parent to refetch
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Add Member to Group">
      <form onSubmit={handleSubmit} className="space-y-4">
        <ErrorMessage message={error} />
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded-md text-sm">
            User added successfully!
          </div>
        )}
        <Input
          label="User Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="e.g., bob@vit.edu"
        />
        <Button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Member'}
        </Button>
      </form>
    </Modal>
  );
};

/**
 * Modal to view balances and make settlements
 */
const ViewBalancesModal = ({ show, onClose, groupId, balancesData, members, onSettlementMade }) => {
  const { user } = useAuth();
  const [toUserId, setToUserId] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { settlements = [], balances = {} } = balancesData || {};

  // Create a map of member IDs to names for easy lookup
  const memberMap = useMemo(() => {
    const map = new Map();
    members.forEach(m => map.set(m.id, m.name));
    return map;
  }, [members]);

  // Find people the current user needs to pay
  const debts = settlements.filter(s => s.from === user.id);

  useEffect(() => {
    if (debts.length > 0) {
      setToUserId(debts[0].to);
      setAmount(debts[0].amount.toFixed(2));
    } else {
      setToUserId('');
      setAmount('');
    }
  }, [balancesData, show]);

  const handleSubmitSettlement = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post('/settlements', {
        groupId,
        toUserId,
        amount: parseFloat(amount),
      });
      onSettlementMade(); // Refetch
      setAmount('');
      setToUserId('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Group Balances">
      <div className="space-y-6">
        {/* --- Section 1: Simplified Debts --- */}
        <div>
          <h4 className="text-lg font-semibold text-gray-800 mb-2">Who Owes Whom</h4>
          <div className="space-y-2">
            {settlements.length === 0 ? (
              <p className="text-gray-500">Everyone is settled up!</p>
            ) : (
              settlements.map((s, index) => (
                <div key={index} className="flex items-center p-2 bg-gray-50 rounded-md">
                  <span className="font-medium text-gray-700">
                    {memberMap.get(s.from) || 'Someone'}
                  </span>
                  <span className="mx-2 text-gray-500">&rarr;</span>
                  <span className="font-medium text-gray-700">
                    {memberMap.get(s.to) || 'Someone'}
                  </span>
                  <span className="ml-auto font-bold text-gray-800">
                    ₹{s.amount.toFixed(2)}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* --- Section 2: Make a Payment --- */}
        <div>
          <h4 className="text-lg font-semibold text-gray-800 mb-3 border-t pt-4">Settle Up</h4>
          <form onSubmit={handleSubmitSettlement} className="space-y-4">
            <ErrorMessage message={error} />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">You pay:</label>
              <select
                value={toUserId}
                onChange={(e) => {
                  setToUserId(e.target.value);
                  // Auto-fill amount if it's a known debt
                  const debt = debts.find(d => d.to === e.target.value);
                  setAmount(debt ? debt.amount.toFixed(2) : '');
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a person...</option>
                {members
                  .filter(m => m.id !== user.id) // Can't pay yourself
                  .map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))
                }
              </select>
            </div>
            <Input
              label="Amount (₹)"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Amount to pay"
              disabled={!toUserId}
            />
            <Button type="submit" disabled={loading || !toUserId || !amount}>
              {loading ? 'Sending...' : 'Record Payment'}
            </Button>
          </form>
        </div>
      </div>
    </Modal>
  );
};

/**
 * Group Details Page: Shows expenses, members, and balances
 */
const GroupPage = ({ groupId, onBack }) => {
  const [group, setGroup] = useState(null);
  const [balances, setBalances] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal states
  const [addExpenseModal, setAddExpenseModal] = useState(false);
  const [addMemberModal, setAddMemberModal] = useState(false);
  const [viewBalancesModal, setViewBalancesModal] = useState(false);

  const { user } = useAuth();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const groupData = await api.get(`/groups/${groupId}`);
      const balancesData = await api.get(`/settlements/balances/group/${groupId}`);
      setGroup(groupData);
      setBalances(balancesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [groupId]);

  const handleExpenseDeleted = (expenseId) => {
    setGroup(prev => ({
      ...prev,
      expenses: prev.expenses.filter(e => e.id !== expenseId),
    }));
    // Re-fetch balances as they have changed
    api.get(`/settlements/balances/group/${groupId}`).then(setBalances);
  };

  // Find logged-in user's balance
  const myBalance = balances?.balances[user.id] || 0.0;

  const getBalanceColor = (balance) => {
    if (balance > 0.01) return 'text-green-600';
    if (balance < -0.01) return 'text-red-600';
    return 'text-gray-500';
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <button onClick={onBack} className="text-blue-600 hover:underline mb-4">&larr; Back to Groups</button>
        <Spinner />
      </div>
    );
  }

  if (error || !group) {
    return (
      <div className="container mx-auto p-4">
        <button onClick={onBack} className="text-blue-600 hover:underline mb-4">&larr; Back to Groups</button>
        <ErrorMessage message={error || "Group not found."} />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-5xl">
      {/* --- Modals --- */}
      <AddExpenseModal
        show={addExpenseModal}
        onClose={() => setAddExpenseModal(false)}
        groupId={groupId}
        members={group.members}
        onExpenseAdded={fetchData} // Refetch all data
      />
      <AddMemberModal
        show={addMemberModal}
        onClose={() => setAddMemberModal(false)}
        groupId={groupId}
        onMemberAdded={fetchData} // Refetch all data
      />
      <ViewBalancesModal
        show={viewBalancesModal}
        onClose={() => setViewBalancesModal(false)}
        groupId={groupId}
        balancesData={balances}
        members={group.members}
        onSettlementMade={fetchData} // Refetch all data
      />

      {/* --- Header --- */}
      <button onClick={onBack} className="text-blue-600 hover:underline mb-4">&larr; Back to Groups</button>
      <div className="flex flex-col sm:flex-row justify-between sm:items-center mb-6 gap-4">
        <h2 className="text-3xl font-bold text-gray-800">{group.name}</h2>
        <div className="flex space-x-2">
          <button onClick={() => setAddExpenseModal(true)} className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 shadow-sm transition-all text-sm">Add Expense</button>
          <button onClick={() => setAddMemberModal(true)} className="px-4 py-2 bg-gray-600 text-white font-semibold rounded-md hover:bg-gray-700 shadow-sm transition-all text-sm">Add Member</button>
        </div>
      </div>

      {/* --- Balance Summary --- */}
      <div className="mb-6 p-4 bg-white shadow rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Your Balance</h3>
        <p className={`text-3xl font-bold ${getBalanceColor(myBalance)}`}>
          {myBalance > 0.01 ? 'You are owed' : myBalance < -0.01 ? 'You owe' : 'You are settled up'}
        </p>
        <p className={`text-3xl font-bold ${getBalanceColor(myBalance)} mb-3`}>
          ₹{Math.abs(myBalance).toFixed(2)}
        </p>
        <button
          onClick={() => setViewBalancesModal(true)}
          className="px-4 py-2 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 shadow-sm transition-all text-sm"
        >
          View Balances & Settle Up
        </button>
      </div>

      {/* --- Main Content (Grid) --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* --- Expenses List --- */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Expenses</h3>
          <div className="space-y-4">
            {group.expenses.length === 0 ? (
              <p className="text-gray-500">No expenses added yet.</p>
            ) : (
              group.expenses.map(expense => (
                <ExpenseItem key={expense.id} expense={expense} onExpenseDeleted={handleExpenseDeleted} />
              ))
            )}
          </div>
        </div>

        {/* --- Members List --- */}
        <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md border border-gray-200 self-start">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Group Members</h3>
          <ul className="space-y-3">
            {group.members.map(member => (
              <li key={member.id} className="flex items-center space-x-3">
                <span className="flex items-center justify-center h-8 w-8 rounded-full bg-blue-100 text-blue-600 font-semibold">
                  {member.name.charAt(0)}
                </span>
                <div>
                  <p className="font-medium text-gray-700">{member.name}</p>
                  <p className="text-sm text-gray-500">{member.email}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GroupPage;
