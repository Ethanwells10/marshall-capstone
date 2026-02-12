import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { athletesAPI } from '../lib/api';

export default function Admin() {
  const queryClient = useQueryClient();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingAthlete, setEditingAthlete] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    grade: '',
    personal_record: '',
    team: 'Jones County',
  });

  const { data: athletes, isLoading, error } = useQuery({
    queryKey: ['athletes'],
    queryFn: async () => {
      const response = await athletesAPI.getAll();
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (newAthlete) => athletesAPI.create(newAthlete),
    onSuccess: () => {
      queryClient.invalidateQueries(['athletes']);
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => athletesAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['athletes']);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => athletesAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['athletes']);
    },
  });

  const resetForm = () => {
    setFormData({ name: '', grade: '', personal_record: '', team: 'Jones County' });
    setIsFormOpen(false);
    setEditingAthlete(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const athleteData = {
      ...formData,
      grade: parseInt(formData.grade, 10),
    };
    if (editingAthlete) {
      updateMutation.mutate({ id: editingAthlete.id, data: athleteData });
    } else {
      createMutation.mutate(athleteData);
    }
  };

  const handleEdit = (athlete) => {
    setEditingAthlete(athlete);
    setFormData({
      name: athlete.name,
      grade: athlete.grade,
      personal_record: athlete.personal_record,
      team: athlete.team,
    });
    setIsFormOpen(true);
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this athlete?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800">Error: {error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Admin Dashboard</h1>
        <button
          onClick={() => setIsFormOpen(true)}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          Add New Athlete
        </button>
      </div>

      {/* Add/Edit Form */}
      {isFormOpen && (
        <div className="mb-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {editingAthlete ? 'Edit Athlete' : 'Add New Athlete'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label htmlFor="grade" className="block text-sm font-medium text-gray-700 mb-2">
                  Grade
                </label>
                <input
                  type="text"
                  id="grade"
                  value={formData.grade}
                  onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label htmlFor="personal_record" className="block text-sm font-medium text-gray-700 mb-2">
                  Personal Record
                </label>
                <input
                  type="text"
                  id="personal_record"
                  value={formData.personal_record}
                  onChange={(e) => setFormData({ ...formData, personal_record: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 16:45"
                  required
                />
              </div>
              <div>
                <label htmlFor="team" className="block text-sm font-medium text-gray-700 mb-2">
                  Team
                </label>
                <input
                  type="text"
                  id="team"
                  value={formData.team}
                  onChange={(e) => setFormData({ ...formData, team: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:bg-blue-300 disabled:cursor-not-allowed font-semibold"
              >
                {createMutation.isPending || updateMutation.isPending
                  ? 'Saving...'
                  : editingAthlete
                  ? 'Update Athlete'
                  : 'Add Athlete'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition font-semibold"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Athletes Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Grade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Personal Record
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Team
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {athletes?.map((athlete) => (
                <tr key={athlete.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {athlete.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {athlete.grade}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {athlete.personal_record}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {athlete.team}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(athlete)}
                        className="bg-blue-100 text-blue-700 px-3 py-1 rounded hover:bg-blue-200 transition font-semibold"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(athlete.id)}
                        disabled={deleteMutation.isPending}
                        className="bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 transition disabled:bg-red-50 disabled:cursor-not-allowed font-semibold"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
