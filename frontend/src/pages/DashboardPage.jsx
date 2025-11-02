import { useState, useEffect } from 'react';
import { api } from '../api/api';
import Spinner from '../components/ui/Spinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import Modal from '../components/ui/Modal';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

/**
 * Modal to create a new group
 */
const CreateGroupModal = ({ show, onClose, onGroupCreated }) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const newGroup = await api.post('/groups', { name });
      onGroupCreated(newGroup);
      setName(''); // Reset form
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Create New Group">
      <form onSubmit={handleSubmit} className="space-y-4">
        <ErrorMessage message={error} />
        <Input
          label="Group Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Trip to Goa"
        />
        <Button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Group'}
        </Button>
      </form>
    </Modal>
  );
};

/**
 * Dashboard Page: Lists all user's groups
 */
const DashboardPage = ({ onViewGroup }) => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const data = await api.get('/groups/user');
      setGroups(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleGroupCreated = (newGroup) => {
    // Add member count to the new group object
    const groupWithCount = { ...newGroup, _count: { members: 1 } };
    setGroups([groupWithCount, ...groups]);
    setIsModalOpen(false);
  };

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Your Groups</h2>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-5 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 shadow-sm transition-all"
        >
          + Create Group
        </button>
      </div>

      <CreateGroupModal
        show={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onGroupCreated={handleGroupCreated}
      />

      {loading && <Spinner />}
      <ErrorMessage message={error} />

      {!loading && groups.length === 0 && (
        <div className="text-center p-10 bg-gray-50 rounded-lg">
          <h3 className="text-xl font-semibold text-gray-700">No groups found</h3>
          <p className="text-gray-500 mt-2">Click "Create Group" to get started!</p>
        </div>
      )}

      <div className="space-y-4">
        {groups.map(group => (
          <div
            key={group.id}
            onClick={() => onViewGroup(group.id)}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all cursor-pointer border border-gray-200"
          >
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-800">{group.name}</h3>
              <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                {group._count?.members || 1} member{group._count?.members > 1 ? 's' : ''}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DashboardPage;
